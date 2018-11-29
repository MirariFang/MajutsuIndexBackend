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
        if gender == 'male':
            gender = 1
        elif gender == 'female':
            gender = 2
        else:
            gender = 3
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
        email = request.GET.get('UserEmail')
        query_dict = None
        with connection.cursor() as cursor:
            cursor.execute('SELECT animeID, name, imageLink FROM Anime')
            animes = tuple_to_list(cursor.fetchall())
            #atrributes = cursor.description
            cursor.execute('SELECT animeID FROM LikeAnime WHERE email = %s', [email])
            likes = tuple_to_list(cursor.fetchall())
            cursor.execute('SELECT animeID, status FROM WatchStatus WHERE email = %s', [email])
            watch = tuple_to_list(cursor.fetchall())
        for i in animes:
            i.append([i[0]] in likes)
            flag = True
            for j in watch:
                if i[0] == j[0]:
                    i.append(str(j[1]))
                    flag = False
                    break
            if flag:
                i.append('0')
        # print(atrributes)
        # columns = [col[0] for col in atrributes].append('likestatus')
        # print(columns)
        # columns.append('watchstatus')
        columns = ['animeID', 'name', 'imageLink', 'likestatus', 'watchstatus']
        query_dict = [dict(zip(columns, row)) for row in animes]
            # query_dict = dictfetchall(cursor)
        if query_dict is not None:
            return HttpResponse(json.dumps(query_dict))
        else:
            return HttpResponse('empty')
    
    return HttpResponse('Anime display placeholder')

@csrf_exempt
def detail_page(request):
    if request.method == 'GET':
        email = request.GET.get('UserEmail')
        animeID = request.GET.get('animeID')

        with connection.cursor() as cursor:
            cursor.execute('''
            SELECT animeID, name, imageLink, releaseDate, releaseYear, episode, studio, director, tags 
            FROM Anime
            WHERE animeID = %s''', [animeID])
            animes = tuple_to_list(cursor.fetchall())
            cursor.execute('SELECT animeID FROM LikeAnime WHERE email = %s AND animeID = %s', [email, animeID])
            likes = tuple_to_list(cursor.fetchall())
            cursor.execute('SELECT animeID, status FROM WatchStatus WHERE email = %s AND animeID = %s', [email, animeID])
            watch = tuple_to_list(cursor.fetchall())
            cursor.execute('SELECT animeID, rate FROM RateAnime WHERE email = %s AND animeID = %s', [email, animeID])
            userrate = tuple_to_list(cursor.fetchall())
            cursor.execute('''
            SELECT animeID, AVG(rate) 
            FROM RateAnime 
            GROUP BY animeID
            HAVING animeID = %s''', [animeID])
            rate = tuple_to_list(cursor.fetchall())
        for i in animes:
            i.append([i[0]] in likes)
            flag = True
            for j in watch:
                if i[0] == j[0]:
                    i.append(str(j[1]))
                    flag = False
                    break
            if flag:
                i.append('0')
            flag = True
            for j in rate:
                if i[0] == j[0]:
                    i.append(str(j[1]))
                    flag = False
                    break
            if flag:
                i.append('0')
            flag = True
            for j in userrate:
                if i[0] == j[0]:
                    i.append(int(j[1]))
                    flag = False
                    break
            if flag:
                i.append('0')
        columns = ['animeID', 'name', 'imageLink', 'releaseDate', 'releaseYear', 'episode', 'studio', 'director', 'tags', 'likestatus', 'watchstatus', 'rate', 'userrate']
        query_dict = [dict(zip(columns, row)) for row in animes]
        if query_dict is not None:
            return HttpResponse(json.dumps(query_dict))
        else:
            return HttpResponse('empty')
    
    return HttpResponse('Detail_page placeholder')

@csrf_exempt
def recommend(request):
    if request.method == 'GET':
        email = request.GET.get('UserEmail')

        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TEMPORARY TABLE s AS
                (SELECT t.tag, COUNT(t.animeID) AS ct
                FROM LikeAnime l JOIN Anime_Tag t ON l.animeID = t.animeID
                WHERE l.email = %s 
                GROUP BY t.tag);
                ''', [email])
            cursor.execute('''
                CREATE TEMPORARY TABLE m AS 
                (SELECT t.animeID, SUM(s.ct) AS sum 
                FROM s JOIN Anime_Tag t ON s.tag = t.tag 
                GROUP BY t.animeID);
            ''')
            cursor.execute('''
                SELECT a.animeID, a.name, a.imageLink 
                FROM m JOIN Anime a ON m.animeID = a.animeID 
                WHERE a.animeID NOT IN 
                    (SELECT l.animeID FROM LikeAnime l WHERE l.email = %s) 
                    AND a.animeID NOT IN 
                    (SELECT w.animeID FROM WatchStatus w WHERE w.email = %s) 
                ORDER BY m.sum DESC;
            ''', [email, email])
            animes = tuple_to_list(cursor.fetchall())
            # cursor.execute('SELECT animeID FROM LikeAnime WHERE email = %s', [email])
            # likes = tuple_to_list(cursor.fetchall())
            # cursor.execute('SELECT animeID, status FROM WatchStatus WHERE email = %s', [email])
            # watch = tuple_to_list(cursor.fetchall())
            for i in animes:
                # i.append([i[0]] in likes)
                # flag = True
                # for j in watch:
                #     if i[0] == j[0]:
                #         i.append(str(j[1]))
                #         flag = False
                #         break
                #     if flag:
                #         i.append('0')
                i.append(0)
                i.append('0')
            columns = ['animeID', 'name', 'imageLink', 'likestatus', 'watchstatus']
            query_dict = [dict(zip(columns, row)) for row in animes]
        if query_dict is not None:
            return HttpResponse(json.dumps(query_dict))
        else:
            return HttpResponse('empty')

    return HttpResponse('Recommend tab placeholder')

@csrf_exempt
def popular(request):
    if request.method == 'GET':
        email = request.GET.get('UserEmail')

        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TEMPORARY TABLE k AS 
                (SELECT l.animeID, COUNT(l.email) AS ct 
                FROM LikeAnime l 
                GROUP BY l.animeID);
                ''')
            cursor.execute('''
            CREATE TEMPORARY TABLE s AS 
                (SELECT r.animeID, AVG(r.rate) AS avg 
                FROM RateAnime r 
                GROUP BY r.animeID);
            ''')
            cursor.execute('''
            CREATE TEMPORARY TABLE n AS 
                (SELECT w.animeID, COUNT(w.email) AS ct 
                FROM WatchStatus w 
                WHERE w.status >= 1 AND w.status <= 3 
                GROUP BY w.animeID);
            ''')
            cursor.execute('''
            CREATE TEMPORARY TABLE m AS 
                (SELECT s.animeID, s.avg + 4 * EXP(-1/k.ct) + 2 * EXP(-1/n.ct) AS score 
                FROM s JOIN k ON s.animeID = k.animeID JOIN n ON k.animeID = n.animeID);
            ''')
            cursor.execute('''
            SELECT a.animeID, a.name, a.imageLink 
                FROM m JOIN Anime a ON m.animeID = a.animeID
                ORDER BY m.score DESC
                LIMIT 50;
            ''')
            animes = tuple_to_list(cursor.fetchall())
            cursor.execute('SELECT animeID FROM LikeAnime WHERE email = %s', [email])
            likes = tuple_to_list(cursor.fetchall())
            cursor.execute('SELECT animeID, status FROM WatchStatus WHERE email = %s', [email])
            watch = tuple_to_list(cursor.fetchall())
            for i in animes:
                i.append([i[0]] in likes)
                flag = True
                for j in watch:
                    if i[0] == j[0]:
                        i.append(str(j[1]))
                        flag = False
                        break
                    if flag:
                        i.append('0')
            columns = ['animeID', 'name', 'imageLink', 'likestatus', 'watchstatus']
            query_dict = [dict(zip(columns, row)) for row in animes]
        if query_dict is not None:
            return HttpResponse(json.dumps(query_dict))
        else:
            return HttpResponse('empty')

    return HttpResponse('Popular tab placeholder')

@csrf_exempt
def wishlist(request):
    if request.method == 'GET':
        email = request.GET.get('UserEmail')

        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT a.animeID, a.name, a.imageLink 
                FROM Anime a JOIN WatchStatus w on a.animeID = w.animeID
                WHERE w.email = %s AND w.status = 1''', [email])
            results = tuple_to_list(cursor.fetchall())
            # atrributes = cursor.description
            cursor.execute('SELECT animeID FROM LikeAnime WHERE email = %s', [email])
            likes = tuple_to_list(cursor.fetchall())
            for i in results:
                i.append([i[0]] in likes)
                i.append('1')
            columns = ['animeID', 'name', 'imageLink', 'likestatus', 'watchstatus']
            query_dict = [dict(zip(columns, row)) for row in results]
        if query_dict is not None:
            return HttpResponse(json.dumps(query_dict))
        else:
            return HttpResponse('empty')

    return HttpResponse('Wishlist tab placeholder')

@csrf_exempt
def watched(request):
    if request.method == 'GET':
        email = request.GET.get('UserEmail')

        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT a.animeID, a.name, a.imageLink 
                FROM Anime a JOIN WatchStatus w on a.animeID = w.animeID
                WHERE w.email = %s AND w.status = 3''', [email])
            results = tuple_to_list(cursor.fetchall())
            # atrributes = cursor.description
            cursor.execute('SELECT animeID FROM LikeAnime WHERE email = %s', [email])
            likes = tuple_to_list(cursor.fetchall())
            for i in results:
                i.append([i[0]] in likes)
                i.append('3')
            columns = ['animeID', 'name', 'imageLink', 'likestatus', 'watchstatus']
            query_dict = [dict(zip(columns, row)) for row in results]
        if query_dict is not None:
            return HttpResponse(json.dumps(query_dict))
        else:
            return HttpResponse('empty')

    return HttpResponse('Watched tab placeholder')

@csrf_exempt
def watching(request):
    if request.method == 'GET':
        email = request.GET.get('UserEmail')

        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT a.animeID, a.name, a.imageLink 
                FROM Anime a JOIN WatchStatus w on a.animeID = w.animeID
                WHERE w.email = %s AND w.status = 2''', [email])
            results = tuple_to_list(cursor.fetchall())
            # atrributes = cursor.description
            cursor.execute('SELECT animeID FROM LikeAnime WHERE email = %s', [email])
            likes = tuple_to_list(cursor.fetchall())
            for i in results:
                i.append([i[0]] in likes)
                i.append('2')
            columns = ['animeID', 'name', 'imageLink', 'likestatus', 'watchstatus']
            query_dict = [dict(zip(columns, row)) for row in results]
        if query_dict is not None:
            return HttpResponse(json.dumps(query_dict))
        else:
            return HttpResponse('empty')

    return HttpResponse('Watching tab placeholder')

@csrf_exempt
def search(request):
    if request.method == 'GET':
        email = request.GET.get('UserEmail')
        keyword = request.GET.get('value')

        query_dict = None
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT animeID, name, imageLink 
                FROM Anime 
                WHERE name LIKE %s''', ['%'+keyword+'%'])
            results = tuple_to_list(cursor.fetchall())
            # atrributes = cursor.description
            cursor.execute('SELECT animeID FROM LikeAnime WHERE email = %s', [email])
            likes = tuple_to_list(cursor.fetchall())
            cursor.execute('SELECT animeID, status FROM WatchStatus WHERE email = %s', [email])
            watch = tuple_to_list(cursor.fetchall())
            for i in results:
                i.append([i[0]] in likes)
                flag = True
                for j in watch:
                    if i[0] == j[0]:
                        i.append(str(j[1]))
                        flag = False
                        break
                if flag:
                    i.append('0')
            columns = ['animeID', 'name', 'imageLink', 'likestatus', 'watchstatus']
            query_dict = [dict(zip(columns, row)) for row in results]
            # query_dict = dictfetchall(cursor)
        if query_dict is not None:
            return HttpResponse(json.dumps(query_dict))
        else:
            return HttpResponse('empty')

    return HttpResponse('Search tab placeholder')

@csrf_exempt
def search_fav(request):
    if request.method == 'GET':
        email = request.GET.get('UserEmail')
        keyword = request.GET.get('name')

        query_dict = None
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT a.animeID, a.name, a.imageLink 
                FROM Anime a JOIN LikeAnime l on a.animeID = l.animeID
                WHERE a.email=%s AND a.name LIKE %s''', [email, '%'+keyword+'%'])
            results = tuple_to_list(cursor.fetchall())
            # atrributes = cursor.description
            cursor.execute('SELECT animeID, status FROM WatchStatus WHERE email = %s', [email])
            watch = tuple_to_list(cursor.fetchall())
            for i in results:
                i.append(1)
                flag = True
                for j in watch:
                    if i[0] == j[0]:
                        i.append(str(j[1]))
                        flag = False
                        break
                if flag:
                    i.append('0')
            columns = ['animeID', 'name', 'imageLink', 'likestatus', 'watchstatus']
            query_dict = [dict(zip(columns, row)) for row in results]
            # query_dict = dictfetchall(cursor)
        if query_dict is not None:
            return HttpResponse(json.dumps(query_dict))
        else:
            return HttpResponse('empty')

    return HttpResponse('Search_fav tab placeholder')

@csrf_exempt
def fav(request):
    if request.method == 'GET':
        email = request.GET.get('UserEmail')
        with connection.cursor() as cursor:
            # Return full fav list
            cursor.execute(
                'SELECT DISTINCT a.animeID AS animeID, a.name AS name, a.imageLink AS imageLink FROM Anime AS a, LikeAnime AS l WHERE l.email = %s AND l.animeID = a.animeID',
                [email])
            fav = tuple_to_list(cursor.fetchall())
            cursor.execute('SELECT animeID, status FROM WatchStatus WHERE email = %s', [email])
            watch = tuple_to_list(cursor.fetchall())
            for i in fav:
                i.append(1)
                flag = True
                for j in watch:
                    if i[0] == j[0]:
                        i.append(str(j[1]))
                        flag = False
                        break
                if flag:
                    i.append('0')
            columns = ['animeID', 'name', 'imageLink', 'likestatus', 'watchstatus']
            query_dict = [dict(zip(columns, row)) for row in fav]
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
        email = request.GET.get('UserEmail')
        # keyword = request.GET.get('name')
        animeID = request.GET.get('animeID')
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
            # Return full watchstatus list
            cursor.execute(
                'SELECT DISTINCT a.animeID AS animeID, a.name AS name FROM Anime AS a, WatchStatus AS w WHERE w.email = %s AND w.animeID = a.animeID',
                [email])
            query_dict = dictfetchall(cursor)
            if query_dict is not None:
                return HttpResponse(json.dumps(query_dict))
            else:
                return HttpResponse('empty')
    
    return HttpResponse('Change anime watching status')

# For debug purpose
@csrf_exempt
def debug_json(request):
    if request.method == 'POST':
        a = [{'parent_id': None, 'id': 54360982}, {'parent_id': None, 'id': 54360880}]
        return HttpResponse(json.dumps(a))
    else:
        return HttpResponse('Placeholder')

@csrf_exempt
def rate(request):
    if request.method == 'POST':
        json_data = post_json(request)
        email = json_data['email']
        animeID = json_data['animeID']
        rate = json_data['userrate']
        with connection.cursor() as cursor:
            cursor.execute('SELECT rate FROM RateAnime WHERE email = %s AND animeID = %s', [email, animeID])
            if cursor.fetchone() is None:
                cursor.execute('INSERT INTO RateAnime (email, animeID, rate) VALUES (%s, %s, %s)', [email, animeID, rate])
            else:
                cursor.execute('UPDATE RateAnime SET rate = %s WHERE email = %s AND animeID = %s',[rate, email, animeID])
            return HttpResponse('OK')

@csrf_exempt
def date(request):
    email = request.GET.get('UserEmail')
    # year is a string
    year = request.GET.get('year')
    # month is a string
    month = request.GET.get('month')
    year = int(year)
    month = int(month)
    monthMapList = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month = monthMapList[month - 1]

    query_dict = None
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT animeID, name, imageLink 
            FROM Anime 
            WHERE releaseDate LIKE %s AND releaseYear = %s''', ['%'+month, year])
        results = tuple_to_list(cursor.fetchall())
        # atrributes = cursor.description
        cursor.execute('SELECT animeID FROM LikeAnime WHERE email = %s', [email])
        likes = tuple_to_list(cursor.fetchall())
        cursor.execute('SELECT animeID, status FROM WatchStatus WHERE email = %s', [email])
        watch = tuple_to_list(cursor.fetchall())
        for i in results:
            i.append([i[0]] in likes)
            flag = True
            for j in watch:
                if i[0] == j[0]:
                    i.append(j[1])
                    flag = False
                    break
            if flag:
                i.append(0)
        columns = ['animeID', 'name', 'imageLink', 'likestatus', 'watchstatus']
        query_dict = [dict(zip(columns, row)) for row in results]
        # query_dict = dictfetchall(cursor)
    if query_dict is not None:
        return HttpResponse(json.dumps(query_dict))
    else:
        return HttpResponse('empty')

@csrf_exempt
def anime_like(request):
    email = request.GET.get('UserEmail')
    animeID = request.GET.get('animeID')
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT * FROM LikeAnime WHERE email = %s AND animeID = %s
        ''', [email, animeID])
        if cursor.fetchone() is None:
            return HttpResponse(json.dumps({'likestatus': 0}))
        else:
            return HttpResponse(json.dumps({'likestatus': 1}))
        