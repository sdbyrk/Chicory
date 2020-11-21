from django.db import models

# Create your models here.
class Member(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    watchedMovie = models.ManyToManyField('movieApp.Movie', blank=True, related_name='watchedMovie', verbose_name="İzlenen Filmler")    
    watchLater = models.ManyToManyField('movieApp.Movie',  blank=True, related_name='watchLater', verbose_name="İzlenecek Filmler")    
    recommendedMovie = models.ManyToManyField('movieApp.Movie',  blank=True, related_name='suggestionMovie', verbose_name="Önerilen Filmler")

    def __str__(self):
    	return self.user.username

class Relationship(models.Model):
	member = models.OneToOneField('user.Member', on_delete=models.CASCADE)
	follower = models.ManyToManyField('user.Member', related_name='follower', verbose_name="Takipçiler")
	followed = models.ManyToManyField('user.Member', related_name='followed', verbose_name="Takip Edilenler")

	def __str__(self):
		return self.member.user.username