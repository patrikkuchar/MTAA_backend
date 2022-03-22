
from itsdangerous import Serializer
import psycopg2 as psycopg2
import os
import json
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.shortcuts import render
from django.db import models
import json

from django.forms.models import model_to_dict


from app.models import Booking, Liked, User, Property

SECRET_KEY = os.getenv('SECRET_KEY')



# Create your views here.
def homepage(request):
    query = "SELECT * FROM users;"

    cur.execute(query)

    result = cur.fetchall()

    object = {'object': []}

    for row in result:
        object["object"].append({
            'id': row[0],
            'name': row[1],
            'surname': row[2],
            'email': row[3],
            'password': row[4]
        })

    return JsonResponse(object)

def postTest(request):
    html = "<h1>OK</h1>"
    str = request.body.decode('utf-8')#.replace("\n","").replace("\r","").replace(" ","")
    d = json.loads(str)
    return HttpResponse(html)





# USER functions
#-------------------------------

# Registering user (adding to database) [POST]
def register_user(request):
    if request.method == 'POST':
        str = request.body.decode('UTF-8')
        dictionary = json.loads(str)

        p = User()

       # p.id = dictionary['id']
        p.name = dictionary['name']
        p.surname = dictionary['surname']
        p.email = dictionary['email']
        p.password = dictionary['password']

        p.save()

    return HttpResponse()

# Logging in user < ++ Working on it>
def login_user(request, email):
   # user = authenticate(email=email, password=password)
    u = User.objects.get(email=email)
    return HttpResponse()
    




#PROPERTY functions
#--------------------------------

# Returning json object from Property [GET]
def property_info(request, property_id):
   
    prop = Property.objects.get(id = property_id)
    prop = model_to_dict(prop)
   
    json_property = json.dumps(prop, indent=4, default=str)
    
    return HttpResponse(json_property)

# Adding new property to database (+ TO DO = images adding ) [POST]
def property_add(request):
    if request.method == 'POST':
        str = request.body.decode('UTF-8')
        dictionary =json.loads(str)

        new_property = Property()

        new_property.rooms = dictionary['rooms']
        new_property.area = dictionary['area']
        new_property.price = dictionary['price']
        new_property.region = dictionary['region']
        new_property.subregion = dictionary['subregion']
        new_property.last_updated = dictionary['last_updated']
        new_property.owner_id = dictionary['owner_id']
        new_property.address = dictionary['info']
        

        new_property.save()

    return HttpResponse()

# Deleting property from database [DELETE]
def property_delete(request,property_id):
    p = Property.objects.get(id = property_id)
    p.delete()

    return HttpResponse()


def property_edit(request,property_id):
    p = Property.objects.get(id = property_id)
    





# BOOKINGS FUNCTIONS
#------------------------------

# Return all user's bookings  [GET]
def booking_info(request,user_id):
    All_bookings = []
    a = Booking.objects.filter(buyer_id = user_id)
    
    for b in a:
        new = model_to_dict(b)
        All_bookings.append(new)
    
    json_booking = json.dumps(All_bookings, indent=4, default=str)

    return HttpResponse(json_booking)

# Create new booking [POST]
def booking_create(request):
    if request.method == 'POST':
       str = request.body.decode('UTF-8')
       dictionary =json.loads(str)

       new_booking = Booking()

       new_booking.property_id = dictionary['property_id']
       new_booking.buyer_id = dictionary['buyer_id']
       new_booking.time = dictionary['time']

       new_booking.save()

    return HttpResponse()

# Delete existing booking [DELETE]
def booking_delete(request,booking_id):
    booking = Booking.objects.get(id == booking_id)
    booking.delete()

    return HttpResponse()





# LIKED FUNCTIONS
#-------------------------------

# Return all user's liked properties [GET]
def liked_info(request,user_id):
    All_liked = []
    all = Liked.objects.filter(user_id = user_id)
    
    for one in all:
        model_liked_one = model_to_dict(one)
        All_liked.append(model_liked_one)

    
    json_liked = json.dumps(All_liked, indent=4, default=str)

    return HttpResponse(json_liked)

# Add property to user's liked properties [POST]
def liked_add(request):
    if request.method == 'POST':
       str = request.body.decode('UTF-8')
       dictionary =json.loads(str)

       new_liked = Liked()

       new_liked.property_id = dictionary['property_id']
       new_liked.user_id = dictionary['user_id']

       new_liked.save()

    return HttpResponse()

# Remove property from user's liked list [DELETE]
def liked_remove(request,liked_id):
    liked = Liked.objects.get(id == liked_id)
    liked.delete()

    return HttpResponse()