from django.db import models

# Create your models here.
class Actor(models.Model):
	name = models.CharField(max_length=50, null=False, verbose_name="Oyuncu İsmi")

	def __str__(self):
		return self.name

class Director(models.Model):
	name = models.CharField(max_length=50, null=False, verbose_name="Yönetmen İsmi")

	def __str__(self):
		return self.name

class Genre(models.Model):
	name = models.CharField(max_length=50, null=False, verbose_name="Tür İsmi")

	def __str__(self):
		return self.name

class Movie(models.Model):
	title = models.CharField(max_length=50, null=False, verbose_name="Başlık")
	poster = models.ImageField(null=True, blank=True, verbose_name="Poster")
	rating = models.FloatField(null=True, blank=True, verbose_name="Puan")
	director = models.ManyToManyField('movieApp.Director', verbose_name="Yönetmen")
	cast = models.ManyToManyField('movieApp.Actor', verbose_name="Oyuncular")
	genre = models.ManyToManyField('movieApp.Genre', verbose_name="Tür")

	def __str__(self):
		return self.title