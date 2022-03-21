import psycopg2 as psycopg2
import os
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render

SECRET_KEY = os.getenv('SECRET_KEY')

conn = psycopg2.connect(database=os.getenv('DATABASE'), user=os.getenv('USER'),
                        password=os.getenv('PASS'), host=os.getenv('HOST'),
                        port=os.getenv('PORT'))
cur = conn.cursor()

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
    return HttpResponse(html)