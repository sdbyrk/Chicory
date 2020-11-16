from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('director/<int:pk>/', views.directorMovies, name='director'),
    path('actor/<int:pk>/', views.actorMovies, name='actor'),
    path('genre/<int:pk>/', views.genreMovies, name='genre'),
]