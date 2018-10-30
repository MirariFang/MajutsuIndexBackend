from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('Home page placeholder')

def login(request):
    return HttpResponse('Login placeholder')

def register(request):
    return HttpResponse('Register page placeholder')

def anime_display(request):
    return HttpResponse('Page that displays all animes with 3 tabs (default: tab 1)')

def recommend(request):
    return HttpResponse('Recommend tab placeholder')

def fav(request):
    return HttpResponse('Fav anime placeholder')