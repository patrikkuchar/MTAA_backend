
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


from app.models import User, Property

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


 
def login_user(request, email):
   # user = authenticate(email=email, password=password)
    u = User.objects.get(email=email)
    return HttpResponse()
    

# Returning json object from Property
def property_info(request, property_id):
   
    prop = Property.objects.get(id = property_id)
    prop = model_to_dict(prop)
   
    json_property = json.dumps(prop, indent=4, default=str)
    
    return HttpResponse(json_property)



# Adding new property to database (+ TO DO = images adding )
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
