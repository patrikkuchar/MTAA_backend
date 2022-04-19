import os
from django.http import JsonResponse
import json
import jwt
import datetime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import base64

from django.forms.models import model_to_dict
from django.db.models import Count

from app.models import Booking, Liked, User, Property, Image, Region, Subregion

SECRET_KEY = os.getenv('SECRET_KEY')


def checkToken(request):
    try:
        token = request.headers["Authorization"]
        token = token.split(' ')[1]  # možno nebude potrebné splitovať, keď to bude volať frontend
    except:
        return None
    try:
        decoded_token = jwt.decode(token, 'secret', algorithms='HS256')
        return decoded_token['id']
    except jwt.ExpiredSignatureError:
        return None
    except:
        return None


# USER functions
# -------------------------------

# Registering user (adding to database) [POST]
def register_user(request):
    if request.method == 'POST':
        str = request.body.decode('UTF-8')
        dictionary = json.loads(str)

        # validacia či nie je email už používaný
        try:
            User.objects.get(email=dictionary['email'])
            return JsonResponse({'message': 'Email already taken'}, status=400)
        except:
            pass

        if len(dictionary['password']) < 8:
            return JsonResponse({'message': 'Password must be at least 8 characters long'}, status=400)

        p = User()

        p.name = dictionary['name']
        p.surname = dictionary['surname']
        p.email = dictionary['email']
        p.password = dictionary['password']

        p.save()
        return JsonResponse({'message': 'Account created'}, status=201)

    return JsonResponse({'message': 'Wrong method'}, status=400)


# Logging in user < ++ Working on it>
def login_user(request):
    if request.method == 'POST':
        str = request.body.decode('utf-8')
        dictionary = json.loads(str)
        try:
            user = User.objects.get(email=dictionary["email"], password=dictionary["password"])
            payload = {
                'id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                'iat': datetime.datetime.utcnow()
            }

            token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')

            dict = {
                'id': user.id,
                'name': user.name,
                'surname': user.surname,
                'email': user.email,
                'token': token
            }

            return JsonResponse(dict, status=200)
        except:
            return JsonResponse({'message': 'Incorrect email or password'}, status=400)

    return JsonResponse({'message': 'Wrong method'}, status=400)

def change_password(request):
    if request.method == 'PATCH':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'msg': 'Unauthorized access'}, status=401)

        str = request.body.decode('UTF-8')
        dictionary = json.loads(str)

        # validacia stareho hesla
        try:
            user = User.objects.get(id=user_id)
            if user.password != dictionary['old_password']:
                return JsonResponse({'msg': 'Incorrect old password'}, status=400)
        except:
            return JsonResponse({'msg': 'Incorrect old password'}, status=400)

        # validacia hesla
        if len(dictionary['new_password']) < 8:
            return JsonResponse({'msg': 'Password must be at least 8 characters long'}, status=400)

        if dictionary['old_password'] == dictionary['new_password']:
            return JsonResponse({'msg': 'New password must be different from old password'}, status=400)

        if dictionary['new_password'] != dictionary['new_password_confirm']:
            return JsonResponse({'msg': 'Passwords do not match'}, status=400)

        # zmena hesla
        try:
            user = User.objects.get(id=user_id)
            user.password = dictionary['new_password']
            user.save()
            return JsonResponse({'msg': 'Password changed'}, status=204)
        except:
            return JsonResponse({'msg': 'Password change failed'}, status=400)
    return JsonResponse({'msg': 'Wrong method'}, status=400)




# FILTER
def filter(request, parameters):
    if request.method == 'GET':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)

        try:
            parametersList = parameters.split('+')
        except:
            return JsonResponse({'message': 'Wrong parameters'}, status=400)

        if len(parametersList) != 5:
            JsonResponse({'message': 'Bad request1'}, status=400)

        properties = None

        # get property by region
        try:
            if len(parameters) == 4:
                properties = Property.objects.all()
            elif parametersList[0] == "" and parametersList[1] == "":
                subregion = Subregion.objects.all()
            else:
                if int(parametersList[0]) >= 1 and int(parametersList[0]) <= 8 and parametersList[1] == "":
                    subregion = Subregion.objects.filter(region=int(parametersList[0]))
                else:
                    subregion = Subregion.objects.filter(id=int(parametersList[1]))
        except:
            return JsonResponse({'message': 'Bad request2'}, status=400)


        if not properties:
            if parametersList[2] != "":
                priceA, priceB = parametersList[2].split('-')
                priceA = int(priceA)
                priceB = int(priceB)
            else:
                priceA = 0
                priceB = 999999999

            if parametersList[3] != "":
                sizeA, sizeB = parametersList[3].split('-')
                sizeA = int(sizeA)
                sizeB = int(sizeB)
            else:
                sizeA = 0
                sizeB = 999999999

            if parametersList[4] != "":
                rooms = parametersList[4].split('-')
                rooms = [int(i) for i in rooms]
                if 6 in rooms:
                    rooms.append(7,8,9,10,11,12,13)
            else:
                rooms = [1, 2, 3, 4, 5, 6]

            try:
                properties = Property.objects.filter(
                    subregion__in=subregion,
                    price__gte=priceA,
                    price__lte=priceB,
                    area__gte=sizeA,
                    area__lte=sizeB,
                    rooms__in=rooms
                )
            except:
                return JsonResponse({'message': 'Bad request3'}, status=400)

        try:
            filtered_properties = []
            for prop in properties:
                # get owner of property
                owner = User.objects.get(id=prop.owner_id)

                image = Image.objects.get(property_id=prop.id, title=True)

                f = open(image.image_url, 'r')
                img_bytes = f.read()

                filtered_properties.append({
                    "id": prop.id,
                    "rooms": prop.rooms,
                    "area": prop.area,
                    "price": prop.price,
                    "last_updated": prop.last_updated,
                    "address": prop.address,
                    "owner": owner.name + " " + owner.surname,
                    "image": img_bytes
                })

            return JsonResponse({'properties': filtered_properties}, status=200)
        except Exception as e:
            return JsonResponse({'message': 'Bad Request4 ' + str(e)}, status=400)
    return JsonResponse({'message': 'Wrong method'}, status=400)


# PROPERTY functions
# --------------------------------

# Returning json object from Property [GET]
def property_info(request, property_id):
    if request.method == 'GET':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)

        try:
         prop = Property.objects.select_related('owner', 'subregion').get(id=property_id)
        except:
            return JsonResponse({'message': 'Property Not Found'}, status=404)

        region = Region.objects.get(id=prop.subregion.region_id)
        prop_dict = {
            'id': prop.id,
            'rooms': prop.rooms,
            'area': prop.area,
            'price': prop.price,
            'region': region.name,
            'subregion': prop.subregion.name,
            'last_updated': prop.last_updated,
            'address': prop.address,
            'info': prop.info,
            'owner': prop.owner.name + ' ' + prop.owner.surname,
            'owner_id': prop.owner.id
        }

        try:
            images = Image.objects.filter(property=prop)
            images_list = []
            for image in images:
                f = open(image.image_url, 'r')
                img_bytes = f.read()
                #images_list.append(img_bytes)
                images_list.append(img_bytes)
            prop_dict['images'] = images_list
        except:
            prop_dict['images'] = []

        return JsonResponse({'property': prop_dict}, status=200)
    return JsonResponse({'message': 'Wrong method'}, status=400)

# Edit images [POST]
def edit_images(request, property_id):
    if request.method == 'POST':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)

        str = request.body.decode('UTF-8')
        dictionary = json.loads(str)

        if add_images(dictionary["images"], property_id, dictionary["image_title"]):
            return JsonResponse({'message': 'Images added'}, status=201)
        return JsonResponse({'message': 'Images not added'}, status=400)
    return JsonResponse({'message': 'Wrong method'}, status=400)


def add_images(images_add, property_id, title_img):
    try:
        title_img = int(title_img)
    except:
        pass

    try:
        images = Image.objects.filter(property=property_id)
        for image in images:
            default_storage.delete(image.image_url)
            image.delete()
    except:
        pass


    images_arr = []
    try:
        count = 0
        while True:
            images_arr.append(images_add[count])
            count += 1
    except:
        pass

    if len(images_arr) < 2 or title_img >= len(images_arr):
        print("1")
        return False

    try:
        prop = Property.objects.get(id=property_id)
    except:
        print("2")
        return False

    for i, image_bytes in enumerate(images_arr):
        image_url = "app/images/" + str(property_id) + "_" + str(i)
        new_image = Image()


        new_image.property = prop
        new_image.image_url = image_url
        if title_img == i:
            new_image.title = True
        else:
            new_image.title = False

        try:
            with open(image_url, 'w') as f:
                f.write(image_bytes)
        except:
            print("3")
            return False

        new_image.save()

    return True

# Adding new property to database (+ TO DO = images adding ) [POST]
def property_add(request):
    if request.method == 'POST':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)

        str = request.body.decode('UTF-8')
        dictionary = json.loads(str)
        #dictionary = request.POST

        # validate area
        if dictionary['area'] < 0:
            return JsonResponse({'message': 'Area cannot be negative'}, status=400)

        # validate price
        if dictionary['price'] < 0:
            return JsonResponse({'message': 'Price cannot be negative'}, status=400)

        try:
            id1=dictionary['subregion']
            subregion = Subregion.objects.get(id=id1)
        except:
            return JsonResponse({'message': 'Subregion does not exist'}, status=404)

        images = dictionary["images"] 

        new_property = Property()
        new_property.rooms = dictionary['rooms']
        new_property.area = dictionary['area']
        new_property.price = dictionary['price']
        new_property.subregion = subregion
        new_property.last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_property.owner_id = user_id
        new_property.address = dictionary['address']
        new_property.info = dictionary['info']
        new_property.save()

        if not add_images(images, new_property.id, dictionary['title_image']):
            return JsonResponse({'message': 'Error while adding images'}, status=400)

        

        return JsonResponse({'message': 'Property added'}, status=201)
    return JsonResponse({'message': 'Wrong method'}, status=400)

# Get user properties [GET]
def user_properties(request):
    if request.method == 'GET':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)

        try:
            properties = Property.objects.filter(owner_id=user_id)
        except:
            return JsonResponse({'message': 'No properties'}, status=404)

        properties_arr = []
        for property in properties:

            image = Image.objects.get(property_id=property.id, title=True)

            try:
                f = open(image.image_url, 'r')
                img_bytes = f.read()
            except:
                return JsonResponse({'message': 'Error while reading image'}, status=400)

            properties_arr.append({
                "id": property.id,
                "rooms": property.rooms,
                "area": property.area,
                "price": property.price,
                "last_updated": property.last_updated,
                "address": property.address,
                "image": img_bytes
            })

        return JsonResponse({"properties": properties_arr}, status=200)
    return JsonResponse({'message': 'Wrong method'}, status=400)


# Deleting property from database [DELETE]
def property_delete(request, property_id):
    user_id = checkToken(request)
    if user_id is None:
        return JsonResponse({'message': 'Unauthorized access'}, status=401)
    try:
        p = Property.objects.get(id=property_id)
        if p.owner_id != user_id:
            return JsonResponse({'message': 'You do not own this property'}, status=403)
        images = Image.objects.filter(property=property_id)
        for image in images:
            default_storage.delete(image.image_url)
            image.delete()
        booking = Booking.objects.filter(property=property_id)
        for b in booking:
            b.delete()
        liked = Liked.objects.filter(property=property_id)
        for l in liked:
            l.delete()
        p.delete()
        return JsonResponse({'message': 'Property successfully removed'}, status=204)
    except:
        return JsonResponse({'message': 'Not Found'}, status=404)



def property_edit(request, property_id):
    
    user_id = checkToken(request)
    if user_id is None:
        return JsonResponse({'message': 'Unauthorized access'}, status=401)

    str = request.body.decode('UTF-8')
    dictionary = json.loads(str)

    # validate area
    if dictionary['area'] < 0:
        return JsonResponse({'message': 'Area cannot be negative'}, status=400)

    # validate price
    if dictionary['price'] < 0:
        return JsonResponse({'message': 'Price cannot be negative'}, status=400)

    # property in database
    try:
        p = Property.objects.get(id=property_id)
        owner = p.owner_id
        if owner != user_id:
            return JsonResponse({'message': 'You do not own this property'}, status=403)
            
        subregion = Subregion.objects.get(id=dictionary['subregion_id'])
        p.rooms = dictionary['rooms']
        p.area = dictionary['area']
        p.price = dictionary['price']
        p.region = subregion.region
        p.subregion = subregion
        p.last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        p.address = dictionary['info']
        p.save()
        ## doplniť tie obrázky ktoré sa pridajú
        return JsonResponse({'message': 'Property successfully edited'}, status=200)
    except:
        return JsonResponse({'message': 'Not Found'}, status=404)
   


# REGIONS FUNCTIONS
# -----------------------------

def regions(request):
    if request.method == 'GET':
        all_regions=[]
        try:
            regions = Region.objects.all()
           
            for region in regions:
                
                all_regions.append({
                    "id": region.id,
                    "name": region.name,
                })
                    
            regions = {
                "regions": all_regions
            }
            return JsonResponse(regions, safe=False)
            
           

        except:
            return JsonResponse({'message': 'Not Found'}, status=404)
    return JsonResponse({'message': 'Wrong method'}, status=400)


def subregions(request, region_id):
    all_subregions = []
    if request.method == 'GET':
        try:
            subregions = Subregion.objects.filter(region=region_id)
            for subregion in subregions:
                all_subregions.append({
                    "id" : subregion.id,
                    "name": subregion.name,
                })

                print(all_subregions)

            return JsonResponse({'subregions': all_subregions}, status=200)
        except:
            return JsonResponse({'message': 'Not Found'}, status=404)
    return JsonResponse({'message': 'Wrong method'}, status=400)


# BOOKINGS FUNCTIONS
# ------------------------------


def booking_info_create(request):
    if request.method == 'GET' or request.method == 'POST':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)
    else:
        return JsonResponse({'message': 'Wrong method'}, status=400)

    # Return all user's bookings  [GET]
    if request.method == 'GET':
        sell_bookings = []
        buy_bookings = []
        a = Booking.objects.select_related('property', 'buyer')
        for one_booking in a:
            model = model_to_dict(one_booking.property)

            image = Image.objects.get(property_id=one_booking.property.id, title=True)

            f = open(image.image_url, 'r')
            img_bytes = f.read()

            json_property = {
                "id": one_booking.id,
                "rooms": model['rooms'],
                "area": model['area'],
                "price": model['price'],
                "address": model['address'],
                "date": one_booking.time,
                "image": img_bytes
            }

            if one_booking.buyer_id == user_id:  # ktore kupujem
                owner = User.objects.get(id=model['owner'])
                json_property["seller"] = owner.name + " " + owner.surname
                buy_bookings.append(json_property)
            if model['owner'] == user_id:  # ktore predavam
                json_property["buyer"] = one_booking.buyer.name + " " + one_booking.buyer.surname
                sell_bookings.append(json_property)

        return JsonResponse({'buying': buy_bookings, 'selling': sell_bookings}, status=200)

    # Create new booking [POST]
    if request.method == 'POST':
        str = request.body.decode('UTF-8')
        dictionary = json.loads(str)

        new_booking = Booking()

        new_booking.property_id = dictionary['property_id']
        new_booking.buyer_id = user_id
        new_booking.time = dictionary['time']

        new_booking.save()

        return JsonResponse({'message': 'Booking added to database'}, status=201)

def booking_call(request, booking_id):
    if request.method == 'GET':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)

        try:
            booking = Booking.objects.get(id=booking_id)

            return JsonResponse({'message': 'Booking found'}, status=200)
        except:
            return JsonResponse({'message': 'Not Found'}, status=404)
    return JsonResponse({'message': 'Wrong method'}, status=400)


# Delete existing booking [DELETE]
def booking_delete(request, booking_id):
   
    user_id = checkToken(request)
    if user_id is None:
        return JsonResponse({'message': 'Unauthorized access'}, status=401)

    ## Check if user is in booking or if booking exist
    try:
        booking = Booking.objects.get(id=booking_id)
        property = Property.objects.get(id=booking.property_id)

        if not (user_id == booking.buyer_id or user_id == property.owner_id):
            return JsonResponse({'message': 'Unauthorized method'}, status=403)

        booking.delete()
        return JsonResponse({'message': 'Booking deleted'}, status=204)
    except:
        return JsonResponse({'message': 'Booking not Found'}, status=404)

   


# LIKED FUNCTIONS
# -------------------------------

def liked_info_create(request):
    if request.method == 'GET' or request.method == 'POST':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)
    else:
        return JsonResponse({'message': 'Wrong method'}, status=400)

    # Return all user's liked properties [GET]
    if request.method == 'GET':
        All_liked = []
        try:
            all = Liked.objects.select_related('property', 'user').filter(user_id=user_id)
        except:
            return JsonResponse({'message': 'Not Found'}, status=404)

        for one in all:
            image = Image.objects.get(property_id=one.property.id, title=True)

            f = open(image.image_url, 'r')
            img_bytes = f.read()

            model_liked_one = model_to_dict(one.property)
            json_property = {
                "id": model_liked_one['id'],
                "rooms": model_liked_one['rooms'],
                "area": model_liked_one['area'],
                "price": model_liked_one['price'],
                "last_updated": model_liked_one['last_updated'],
                "owner_id": one.user.name + " " + one.user.surname,
                "address": model_liked_one['address'],
                "image": img_bytes
            }
            All_liked.append(json_property)

        return JsonResponse({'properties': All_liked}, status=200)

    # Add property to user's liked properties [POST]
    if request.method == 'POST':
        str = request.body.decode('UTF-8')
        dictionary = json.loads(str)

        try:
            liked = Liked.objects.get(user_id=user_id, property_id=dictionary['property_id'])
            return JsonResponse({'message': 'Already liked'}, status=400)
        except:
            pass

        new_liked = Liked()

        new_liked.property_id = dictionary['property_id']
        new_liked.user_id = user_id

        new_liked.save()

        return JsonResponse({'message': 'Property successfully added to favourites'}, status=201)

def most_liked(request):
    if request.method == 'GET':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)

        All_liked = []
        try:
            all = Liked.objects.all().values('property').annotate(count=Count('property')).order_by('-count')[:5]
        except:
            return JsonResponse({'message': 'Not Found'}, status=404)

        for one in all:
            model_liked_one = model_to_dict(Property.objects.get(id=one.property))

            user = User.objects.get(id=model_liked_one['owner_id'])

            image = Image.objects.get(property_id=model_liked_one.id, title=True)

            f = open(image.image_url, 'r')
            img_bytes = f.read()

            json_property = {
                "id": model_liked_one['id'],
                "rooms": model_liked_one['rooms'],
                "area": model_liked_one['area'],
                "price": model_liked_one['price'],
                "last_updated": model_liked_one['last_updated'],
                "owner_id": user.name + " " + user.surname,
                "address": model_liked_one['address'],
                "image": img_bytes
            }

            All_liked.append(json_property)
        return JsonResponse({'most_liked': All_liked}, status=200)
    return JsonResponse({'message': 'Wrong method'}, status=400)


# Remove property from user's liked list [DELETE]
def liked_remove(request, property_id):
    
    user_id = checkToken(request)
    if user_id is None:
        return JsonResponse({'message': 'Unauthorized access'}, status=401)

    try:
        liked = Liked.objects.get(property_id = property_id, user_id = user_id)
        if user_id != liked.user_id:
            return JsonResponse({'message': 'Unauthorized method'}, status=403)

        liked.delete()
        return JsonResponse({'message': 'Property removed from your favourites'}, status=204)
    except:
        return JsonResponse({'message': 'Not Found'}, status=404)
    
