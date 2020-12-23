from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('order/<int:pk>/', views.order, name='order'),
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('director/<int:pk>/', views.directorMovies, name='director'),
    path('actor/<int:pk>/', views.actorMovies, name='actor'),
    path('genre/<int:pk>/', views.genreMovies, name='genre'),
    path('results', views.searchText, name='search_results'),
    path('recommend/<int:pk>/', views.recommendPage, name='recommend_page'),
    path('movie/<int:pk>/watch', views.watched, name='watched'),
    path('movie/<int:pk>/later', views.later, name='later'),
    path('notifications/recommendMovie/<int:pk>/', views.recommendMovie, name='recommendMovie'),
]