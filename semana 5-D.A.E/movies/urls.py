"""URL configuration for the movies app."""

from django.urls import path

from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.recommendations, name='recommendations'),
    path('movies/search/', views.movie_search, name='movie_search'),
    path('movies/<int:pk>/', views.movie_detail, name='movie_detail'),
]
