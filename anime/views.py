from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
import json
from django.views.decorators.csrf import csrf_exempt
### Custom packages
from anime.utils import post_json
from anime.utils import dictfetchall
from anime.utils import tuple_to_list


# Create your views here.
def index(request):
    return HttpResponse('Home page placeholder')


@csrf_exempt
def login(request):
    if request.method == 'POST':
        json_data = post_json(request)

        email = json_data['email']
        password = json_data['password']
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT Email FROM User WHERE Email = %s AND Password = %s',
                [email, password])
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
        json_data = post_json(request)

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

@csrf_exempt
def anime_display(request):
    if request.method == 'GET':
        json_data = post_json(request)
        email = json_data['email']

        query_dict = None
        with connection.cursor() as anime_cursor:
            anime_cursor.execute('SELECT animeID, name FROM Anime')
        with connection.cursor() as like_cursor:
            like_cursor.execute('SELECT animeID FROM LikeAnime WHERE email = %s', email)
        with connection.cursor() as watch_cursor:
            watch_cursor.execute('SELECT animeID, status FROM WatchStatus WHERE email = %s', email)
        animes = tuple_to_list(anime_cursor.fetchall())
        likes = tuple_to_list(like_cursor.fetchall())
        watch = tuple_to_list(watch_cursor.fetchall())
        for i in animes:
            i.append([i[0]] in likes)
            flag = True
            for j in watch:
            if i[0] in j:
                i.append(j[1])
                flag = False
                break
            if flag:
                i.append(0)
        columns = [col[0] for col in anime_cursor.description].append('likestatus')
        columns.append('watchstatus')
        query_dict = [dict(zip(columns, row)) for row in anime_cursor.fetchall()]
            # query_dict = dictfetchall(cursor)
        if query_dict is not None:
            return HttpResponse(json.dumps(query_dict))
        else:
            return HttpResponse('empty')
    
    return HttpResponse('Anime display placeholder')


def recommend(request):
    return HttpResponse('Recommend tab placeholder')

@csrf_exempt
def fav(request):
    if request.method == 'GET':
        json_data = post_json(request)
        email = json_data['email']
        with connection.cursor() as cursor:
            # Return full fav list
            cursor.execute(
                'SELECT DISTINCT a.animeID AS animeID, a.name AS name FROM Anime AS a, LikeAnime AS l WHERE l.email = %s AND l.animeID = a.animeID',
                [email])
            query_dict = dictfetchall(cursor)
            if query_dict is not None:
                return HttpResponse(json.dumps(query_dict))
            else:
                return HttpResponse('empty')
    elif request.method == 'POST':
        json_data = post_json(request)
        email = json_data['email']
        animeID = json_data['animeID']
        isLike = json_data['action']
        with connection.cursor() as cursor:
            if isLike == 1:
                cursor.execute('SELECT email, animeID FROM LikeAnime WHERE email = %s AND animeID = %s', [email, animeID])
                if cursor.fetchone() is None:
                    cursor.execute('INSERT INTO LikeAnime (email, animeID) VALUES (%s, %s)', [email, animeID])
            else:
                cursor.execute('DELETE FROM LikeAnime WHERE email = %s AND animeID = %s', [email, animeID])
            # Return full fav list
            cursor.execute(
                'SELECT DISTINCT a.animeID AS animeID, a.name AS name FROM Anime AS a, LikeAnime AS l WHERE l.email = %s AND l.animeID = a.animeID',
                [email])
            query_dict = dictfetchall(cursor)
            if query_dict is not None:
                return HttpResponse(json.dumps(query_dict))
            else:
                return HttpResponse('empty')
        
    return HttpResponse('Fav anime placeholder')

@csrf_exempt
def change_watch_status(request):
    if request.method == 'GET':
        json_data = post_json(request)
        email = json_data['email']
        animeID = json_data['animeID']
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT a.animeID AS animeID, a.name AS name, w.status AS watchstatus FROM Anime AS a, WatchStatus AS w WHERE w.email = %s AND w.animeID = %s AND w.animeID = a.animeID',
                [email, animeID])
            query_dict = dictfetchall(cursor)
            if query_dict is not None:
                return HttpResponse(json.dumps(query_dict))
            else:
                return HttpResponse('empty')
    elif request.method == 'POST':
        json_data = post_json(request)
        email = json_data['email']
        animeID = json_data['animeID']
        status = json_data['watchstatus']
        with connection.cursor() as cursor:
            cursor.execute('SELECT status FROM WatchStatus WHERE email = %s AND animeID = %s', [email, animeID])
            if cursor.fetchone() is None:
                cursor.execute('INSERT INTO WatchStatus (email, animeID, status) VALUES (%s, %s, %s)', [email, animeID, status])
            else:
                cursor.execute('UPDATE WatchStatus SET status = %s WHERE email = %s AND animeID = %s',[status, email, animeID])
        return HttpResponse('Change status OK')
    
    return HttpResponse('Change anime watching status')

# For debug purpose
@csrf_exempt
def debug_json(request):
    if request.method == 'POST':
        a = [{'parent_id': None, 'id': 54360982}, {'parent_id': None, 'id': 54360880}]
        return HttpResponse(json.dumps(a))
    else:
        return HttpResponse('Placeholder')