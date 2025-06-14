from django.urls import path
from . import views

urlpatterns = [
    path('genre-prediction/', views.genre_prediction, name='genre_prediction'),
    path('actor-prediction/', views.actor_prediction, name='actor_prediction'),
    path('top-movies/', views.top_movies, name='top_movies'),
]