import code
from pyexpat import model
from types import CodeType
from itsdangerous import Serializer
import psycopg2 as psycopg2
import os
import json
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import models
import json
import jwt
import datetime

from django.forms.models import model_to_dict

from app.models import Booking, Liked, User, Property

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

            return JsonResponse({'jwt': token}, status=200)
        except:
            return JsonResponse({'message': 'Incorrect email or password'}, status=400)

    return JsonResponse({'message': 'Wrong method'}, status=400)

def change_password(request):
    if request.method == 'PATCH':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)

        str = request.body.decode('UTF-8')
        dictionary = json.loads(str)

        # validacia stareho hesla
        try:
            user = User.objects.get(id=user_id)
            if user.password != dictionary['old_password']:
                return JsonResponse({'message': 'Incorrect old password'}, status=400)
        except:
            return JsonResponse({'message': 'Incorrect old password'}, status=400)

        # validacia noveho hesla
        if len(dictionary['new_password']) < 8:
            return JsonResponse({'message': 'Password must be at least 8 characters long'}, status=400)

        # validacia dokoncenia noveho hesla
        if dictionary['new_password'] != dictionary['new_password_confirm']:
            return JsonResponse({'message': 'Passwords do not match'}, status=400)

        # zmena hesla
        try:
            user = User.objects.get(id=user_id)
            user.password = dictionary['new_password']
            user.save()
            return JsonResponse({'message': 'Password changed'}, status=200)
        except:
            return JsonResponse({'message': 'Password change failed'}, status=400)
    return JsonResponse({'message': 'Wrong method'}, status=400)




# FILTER


# PROPERTY functions
# --------------------------------

# Returning json object from Property [GET]
# property/<int:property_id>/
def property_info(request, property_id):
    if request.method == 'GET':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)

        prop = Property.objects.get(id=property_id)
        prop = model_to_dict(prop)

        return JsonResponse(prop, status=200)
    return JsonResponse({'message': 'Wrong method'}, status=400)


# Adding new property to database (+ TO DO = images adding ) [POST]
def property_add(request):
    if request.method == 'POST':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)

        str = request.body.decode('UTF-8')
        dictionary = json.loads(str)

        new_property = Property()

        new_property.rooms = dictionary['rooms']
        new_property.area = dictionary['area']
        new_property.price = dictionary['price']
        new_property.region = dictionary['region']
        new_property.subregion = dictionary['subregion']
        new_property.last_updated = dictionary['last_updated']
        new_property.owner_id = user_id
        new_property.address = dictionary['info']

        new_property.save()

        return JsonResponse({'message': 'Property successfully added'}, status=201)
    return JsonResponse({'message': 'Wrong method'}, status=400)


# Deleting property from database [DELETE]
def property_delete(request, property_id):
    if request.method == 'DELETE':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)

        # property in database
        try:
            p = Property.objects.get(id=property_id)
            if p['owner_id'] != user_id:
                return JsonResponse({'message': 'You do not own this property'}, status=403)

            p.delete()
            return JsonResponse({'message': 'Property successfully removed'}, status=204)
        except:
            return JsonResponse({'message': 'Not Found'}, status=404)
    return JsonResponse({'message': 'Wrong method'}, status=400)


def property_edit(request, property_id):
    if request.method == 'PUT':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)

        str = request.body.decode('UTF-8')
        dictionary = json.loads(str)

        # property in database
        try:
            p = Property.objects.get(id=property_id)
            if p['owner_id'] != user_id:
                return JsonResponse({'message': 'You do not own this property'}, status=403)

            p.rooms = dictionary['rooms']
            p.area = dictionary['area']
            p.price = dictionary['price']
            p.region = dictionary['region']
            p.subregion = dictionary['subregion']
            p.last_updated = dictionary['last_updated']
            p.address = dictionary['info']
            p.save()
            ## doplniť tie obrázky ktoré sa pridajú
            return JsonResponse({'message': 'Property successfully edited'}, status=200)
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

            json_property = {
                "id": model['id'],
                "rooms": model['rooms'],
                "area": model['area'],
                "price": model['price'],
                "address": model['address'],
                "date": one_booking.time
            }

            if one_booking.buyer_id == user_id:  # ktore kupujem
                owner = User.objects.get(id=model['owner_id'])
                json_property["seller"] = owner.name + " " + owner.surname
                buy_bookings.append(json_property)
            if model['owner_id'] == user_id:  # ktore predavam
                json_property["buyer"] = one_booking.buyer.name + " " + one_booking.buyer.surname
                sell_bookings.append(json_property)

        return JsonResponse({'buying': buy_bookings, 'selling': sell_bookings}, status=200)

    # Create new booking [POST]
    if request.method == 'POST':
        str = request.body.decode('UTF-8')
        dictionary = json.loads(str)

        new_booking = Booking()

        new_booking.property_id = dictionary['property_id']
        new_booking.buyer_id = dictionary['buyer_id']
        new_booking.time = dictionary['time']

        new_booking.save()

        return JsonResponse({'message': 'Booking added to database'}, status=201)


# Delete existing booking [DELETE]
def booking_delete(request, booking_id):
    if request.method == 'DELETE':
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

    return JsonResponse({'message': 'Wrong method'}, status=400)


# LIKED FUNCTIONS
# -------------------------------
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
            JsonResponse({'message': 'Bad request'}, status=400)

        if parametersList[0] == "":
            region = r'^.*$'
        else:
            region = r'^' + parametersList[0] + '$'

        if parametersList[1] == "":
            subregion = r'^.*$'
        else:
            subregion = r'^' + parametersList[1] + '$'

        if parametersList[2] != "":
            priceA, priceB = parametersList[2].split('-')
        else:
            priceA = 0
            priceB = 99999999

        if parametersList[3] != "":
            sizeA, sizeB = parametersList[3].split('-')
        else:
            sizeA = 0
            sizeB = 99999999

        if parametersList[4] != "":
            rooms = parametersList[4].split('-')
        else:
            rooms = [1, 2, 3, 4, 5, 6]

        try:
            properties = Property.objects.filter(
                region__regex=region,
                subregion__regex=subregion,
                price__gte=priceA,
                price__lte=priceB,
                area__gte=sizeA,
                area__lte=sizeB,
                rooms__in=rooms
            )

            filtered_properties = []
            for prop in properties:
                # get owner of property
                owner = User.objects.get(id=prop.owner_id)

                filtered_properties.append({
                    "id": prop.id,
                    "rooms": prop.rooms,
                    "area": prop.area,
                    "price": prop.price,
                    "last_updated": prop.last_updated,
                    "address": prop.address,
                    "owner": owner.name + " " + owner.surname
                })

            return JsonResponse({'properties': filtered_properties}, status=201)
        except:
            return JsonResponse({'message': 'Bad Request'}, status=400)
    return JsonResponse({'message': 'Wrong method'}, status=400)


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
        all = Liked.objects.select_related('property', 'user').filter(user_id=user_id)

        for one in all:
            model_liked_one = model_to_dict(one.property)
            json_property = {
                "id": model_liked_one['id'],
                "rooms": model_liked_one['rooms'],
                "area": model_liked_one['area'],
                "price": model_liked_one['price'],
                "last_updated": model_liked_one['last_updated'],
                "owner_id": one.user.name + " " + one.user.surname,
                "address": model_liked_one['address']
            }
            All_liked.append(json_property)

        return JsonResponse({'liked': All_liked}, status=200)

    # Add property to user's liked properties [POST]
    if request.method == 'POST':
        str = request.body.decode('UTF-8')
        dictionary = json.loads(str)

        new_liked = Liked()

        new_liked.property_id = dictionary['property_id']
        new_liked.user_id = user_id

        new_liked.save()

        return JsonResponse({'message': 'Property successfuly added to favourites'}, status=201)


# Remove property from user's liked list [DELETE]
def liked_remove(request, liked_id):
    if request.method == 'DELETE':
        user_id = checkToken(request)
        if user_id is None:
            return JsonResponse({'message': 'Unauthorized access'}, status=401)

        try:
            liked = Liked.objects.get(id=liked_id)
            if user_id != liked.user_id:
                return JsonResponse({'message': 'Unauthorized method'}, status=403)

            liked.delete()
            return JsonResponse({'message': 'Property removed from your favourites'}, status=204)
        except:
            return JsonResponse({'message': 'Not Found'}, status=404)
    return JsonResponse({'message': 'Wrong method'}, status=400)
