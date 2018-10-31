'''Helper functions used in views.py'''
import json
from django.http import HttpRequest, HttpResponse
from django.db import connection

def post_json(request):
    json_data = None
    if request.body:
        json_data = json.loads(request.body)
    return json_data

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def tuple_to_list(t):
    return [list(i) for i in t]
