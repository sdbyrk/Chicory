from django.contrib import admin
from .models import Actor, Director, Genre, Movie
# Register your models here.

admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Genre)
admin.site.register(Movie)