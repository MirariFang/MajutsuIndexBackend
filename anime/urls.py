from django.urls import path
from anime import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('animes/', views.anime_display, name='anime_display'),
    path('animes/recommend/', views.recommend, name='recommend'),
    path('animes/fav/', views.fav, name='favorite'),
]
