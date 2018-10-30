from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
import json
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    return HttpResponse('Home page placeholder')

@csrf_exempt
def login(request):
    if request.method == 'POST':
        json_data = None
        if request.body:
            json_data = json.loads(request.body)

        email = json_data['email']
        password = json_data['password']
        with connection.cursor() as cursor:
            cursor.execute('SELECT Email FROM User WHERE Email = %s AND Password = %s', [email, password])
            row = cursor.fetchone()
            if row is None:
                return HttpResponse("Login failed")
            else:
                return HttpResponse(email)
        return HttpResponse(json_data['email'])
    else:
        return HttpResponse('Login placeholder')


@csrf_exempt
def register(request):
    if request.method == 'POST':
        json_data = None
        if request.body:
            json_data = json.loads(request.body)

        email = json_data['email']
        username = json_data['username']
        password = json_data['password']
        gender = json_data['gender']
        with connection.cursor() as cursor:
            cursor.execute('SELECT Email FROM User WHERE Email = %s', [email])
            row = cursor.fetchone()
            if row is not None:
                return HttpResponse("Register failed")
            cursor.execute(
                'INSERT INTO User (Email, Username, Password, Gender) VALUES (%s, %s, %s, %s)',
                [email, username, password, gender])
        return HttpResponse(json_data['email'])
    else:
        return HttpResponse('Register page placeholder')


def anime_display(request):
    return HttpResponse(
        'Page that displays all animes with 3 tabs (default: tab 1)')


def recommend(request):
    return HttpResponse('Recommend tab placeholder')


def fav(request):
    return HttpResponse('Fav anime placeholder')