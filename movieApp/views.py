from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect

from notifications.signals import notify
import os.path

from .models import Actor, Director, Genre, Movie
from user.models import Member, Relationship
from .forms import RecommendForm


#Get data with BeautifulSoup
def getDataBS(request):

	url = "https://www.imdb.com/chart/top/?ref_=nv_mv_250"

	html = requests.get(url).content

	soup = BeautifulSoup(html, "html.parser")

	liste = soup.find("tbody", {"class": "lister-list"}).find_all("tr")

	for tr in liste:
		title = tr.find("td", {"class": "titleColumn"}).find("a").text
		href = "https://www.imdb.com/" + tr.find("td", {"class":"posterColumn"}).find("a").get("href")
		explanation = requests.get(href).content
		soup = BeautifulSoup(explanation, "html.parser")
		genres = soup.find("div", {"class":"subtext"}).find_all("a")
		rating = soup.find("div", {"class":"ratingValue"}).find("span").text
		poster = soup.find("div", {"class":"poster"}).find("a").find("img").get("src")
		movie = Movie.objects.filter(title=title).first()
		if not movie:
			movie = Movie.objects.create(title=title, poster=poster, rating=rating)

		for genre in genres:
			if not genre.get("title"):
				if not Genre.objects.filter(title=genre.text).first():
					g = Genre.objects.create(title=genre.text)
					movie.genre.add(g)
				else:
					movie.genre.add(Genre.objects.filter(title=genre.text).first())
		plots = soup.find("div", {"class": "plot_summary"}).find_all("div", {"class":"credit_summary_item"})

		for plot in plots:
			h = plot.find("h4").text
			if h == "Director:":
				director = plot.find("a").text
				if not Director.objects.filter(name=director).first():
					d = Director.objects.create(name=director)
					movie.director.add(d)
				else:
					movie.director.add(Director.objects.filter(name=director).first())
			elif h == "Directors:":
				directors = plot.find_all("a")
				for director in directors:
					if not Director.objects.filter(name=director.text).first():
						d = Director.objects.create(name=director.text)
						movie.director.add(d)
					else:
						movie.director.add(Director.objects.filter(name=director.text).first())
			elif h == "Stars:":
				stars = plot.find_all("a")
				for star in stars:
					if star.get("href") != "fullcredits/":
						if not Actor.objects.filter(name=star.text).first():
							a = Actor.objects.create(name=star.text)
							movie.cast.add(a)
						else:
							movie.cast.add(Actor.objects.filter(name=star.text).first())

# Get data with BeautifulSoup and write data to txt file
def siteToFile(request):
	movieFile = open("movieFile.txt","a") 

	url = "https://www.imdb.com/chart/top/?ref_=nv_mv_250"

	html = requests.get(url).content

	soup = BeautifulSoup(html, "html.parser")

	liste = soup.find("tbody", {"class": "lister-list"}).find_all("tr")

	for tr in liste:
		sentence = ""
		title = tr.find("td", {"class": "titleColumn"}).find("a").text
		print(title)
		href = "https://www.imdb.com/" + tr.find("td", {"class":"posterColumn"}).find("a").get("href")
		explanation = requests.get(href).content
		soup = BeautifulSoup(explanation, "html.parser")
		genres = soup.find("div", {"class":"subtext"}).find_all("a")
		rating = soup.find("div", {"class":"ratingValue"}).find("span").text
		poster = soup.find("div", {"class":"poster"}).find("a").find("img").get("src")

		sentence += title + "\t" + poster + "\t" + rating + "\t"
		for genre in genres:
			if not genre.get("title"):
				sentence += genre.text + ","
		plots = soup.find("div", {"class": "plot_summary"}).find_all("div", {"class":"credit_summary_item"})
		
		for plot in plots:
			h = plot.find("h4").text
			if h == "Director:":
				sentence += "\t"
				director = plot.find("a").text
				sentence += director
			elif h == "Directors:":
				sentence += "\t"
				directors = plot.find_all("a")
				for director in directors:
					sentence += director.text + ","
			elif h == "Stars:":
				stars = plot.find_all("a")
				sentence += "\t"
				for star in stars:
					if star.get("href") != "fullcredits/":
						sentence += star.text + ","
		sentence += "\n"
		movieFile.write(sentence)
		print(sentence)
	movieFile.close()

#Get data with txt
def getData(request):
	BASE = os.path.dirname(os.path.abspath(__file__))
	movieFile = open(os.path.join(BASE, "static/movieFile.txt"))
	wrongChars = ["\n", " ", "", "\t"]
	for line in movieFile:
		movieInfo = line.split("\t")
		if movieInfo[0] not in wrongChars:
			title = movieInfo[0]
			poster = movieInfo[1]
			rating = movieInfo[2]
			genres = movieInfo[3]
			directors = movieInfo[4]
			actors = movieInfo[5]
			movie = Movie.objects.filter(title=title).first()
			if not movie:
				movie = Movie.objects.create(title=title, poster=poster, rating=rating)

			for genre in genres.split(","):
				if genre not in wrongChars:
					genreObject = Genre.objects.filter(name=genre).first()
					if not genreObject:
						genreObject = Genre.objects.create(name=genre)
					movie.genre.add(genreObject)

			for director in directors.split(","):
				if director not in wrongChars:
					directorObject = Director.objects.filter(name=director).first()
					if not directorObject:
						directorObject = Director.objects.create(name=director)
					movie.director.add(directorObject)
			for actor in actors.split(","):
				if actor not in wrongChars:
					actorObject = Actor.objects.filter(name=actor).first()
					if not actorObject:
						actorObject = Actor.objects.create(name=actor)
					movie.cast.add(actorObject)

def index(request):
	movies = Movie.objects.all()
	genres = Genre.objects.all()

	return render(request, "movieApp/index.html",
		{"movies": movies, "genres": genres})

def order(request, pk):
	movies = Movie.objects.all()
	genres = Genre.objects.all()

	if pk == 0:
		movies = Movie.objects.all().order_by("title")
	elif pk == 1:
		movies = Movie.objects.all().order_by("-title")
	elif pk == 2:
		movies = Movie.objects.all().order_by("rating")
	else: 
		movies = Movie.objects.all().order_by("-rating")


	return render(request, "movieApp/index.html",
		{"movies": movies, "genres": genres})

def movie_detail(request, pk):
	movie = get_object_or_404(Movie, pk=pk)
	watchedMovies = []
	watchLaters = []
	member = None
	form = None
	if request.user.is_authenticated:
		member = Member.objects.filter(user=request.user).first()
	if member:
		if request.user.is_authenticated:
			watchedMovies = member.watchedMovie.all()
			watchLaters = Member.objects.filter(user=request.user).first().watchLater.all()
	return render(request, "movieApp/movie_detail.html", {"form":form, "movie":movie, "watchedMovies":watchedMovies, "watchLaters":watchLaters})

# Actor's movies
def actorMovies(request, pk):
	filtered = get_object_or_404(Actor, pk=pk)
	movies = Movie.objects.filter(cast__pk=pk)
	genres = Genre.objects.all()
	return render(request, "movieApp/filtered_page.html", {"filtered":filtered, "movies": movies, "genres": genres})

# Director's movies
def directorMovies(request, pk):
	filtered = get_object_or_404(Director, pk=pk)
	movies = Movie.objects.filter(director__pk=pk)
	genres = Genre.objects.all()
	return render(request, "movieApp/filtered_page.html", {"filtered": filtered, "movies": movies, "genres": genres})

# Movies by genre
def genreMovies(request, pk):
	filtered = get_object_or_404(Genre, pk=pk)
	movies = Movie.objects.filter(genre__pk=pk)
	genres = Genre.objects.all()
	return render(request, "movieApp/filtered_page.html", {"filtered": filtered, "movies": movies, "genres": genres})

def searchText(request):
	query = request.GET.get('q')
	search = True
	movies = Movie.objects.all().filter(title__icontains=query)
	actors = Actor.objects.all().filter(name__icontains=query)
	directors = Director.objects.all().filter(name__icontains=query)
	users = User.objects.exclude(username=request.user.username).all().filter(username__icontains=query)
	print(users)
	watchedMovies = []
	return render(request, "movieApp/search_result.html", {"search": search, "movies":movies, "actors": actors, "directors": directors, "watchedMovies":watchedMovies, "users": users})

#Recommending a movie to a followed user
def recommendPage(request, pk):
	print("Hello world")
	member = Member.objects.filter(user=request.user).first()
	movie = get_object_or_404(Movie, pk=pk)
	relation = Relationship.objects.filter(member=member).first()
	followedUsers = None
	if relation:
		followedUsers = relation.followed.all()
	
	if request.method == 'POST':
		form = RecommendForm(request.POST) 
		form.fields["followed"].queryset = followedUsers
		if form.is_valid():
			friend = Member.objects.filter(user__username=form.cleaned_data['followed']).first()
			person = User.objects.filter(username=form.cleaned_data['followed']).first()
			notify.send (request.user, recipient = person, action_object=movie, verb = "filmini önerdi.")
			message = person.username + " kişisine " + movie.title + " filmini önerdiniz."
			messages.add_message(request, messages.SUCCESS, message)
			
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	else:
		form = RecommendForm()
		form.fields["followed"].queryset = followedUsers
	return render(request, "movieApp/recommend_page.html", {"followedUsers": followedUsers, "form": form, "movie": movie})


def recommendMovie(request, pk):
	notification = request.user.notifications.filter(pk=pk).first()
	movie = Movie.objects.filter(title=notification.action_object).first()
	return movie_detail(request, movie.pk)

#Add/remove the movie from the watchedMovies
def watched(request, pk):
	movie = get_object_or_404(Movie, pk=pk)
	member = Member.objects.filter(user=request.user).first()

	if not member:
		member = Member.objects.create(user=request.user)

	watchedMovies = member.watchedMovie.all()
	watchLaters = member.watchLater.all()
	recommendedMovies = Member.objects.filter(user=request.user).first().recommendedMovie.all()
	st = "/movie/" + str(pk) + "/"
	if movie not in watchedMovies:
		if movie in watchLaters:
			member.watchLater.remove(movie)
			watchLaters = member.watchLater.all()
		if movie in recommendedMovies:
			member.recommendedMovie.remove(movie)
		member.watchedMovie.add(movie)
		message = movie.title + " filmi 'İzlenen Filmler' listesine eklendi."
		messages.add_message(request, messages.SUCCESS, message)
		watchedMovies = member.watchedMovie.all()
	else:
		member.watchedMovie.remove(movie)
		message = movie.title + " filmi 'İzlenen Filmler' listesinden çıkarıldı."
		messages.add_message(request, messages.SUCCESS, message)
		watchedMovies = member.watchedMovie.all()
	recommend(request)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#Add/remove the movie from the watchLater
def later(request, pk):
	movie = get_object_or_404(Movie, pk=pk)
	member = Member.objects.filter(user=request.user).first()
	
	if not member:
		member = Member.objects.create(user=request.user)

	watchLaters = member.watchLater.all()
	recommendedMovies = member.recommendedMovie.all()
	
	if movie not in watchLaters:
		member.watchLater.add(movie)
		message = movie.title + " filmi 'İzlenecek Filmler' listesine eklendi."
		messages.add_message(request, messages.SUCCESS, message)
		watchLaters = member.watchLater.all()
		if movie in recommendedMovies:
			member.recommendedMovie.remove(movie)
	else:
		member.watchLater.remove(movie)
		message = movie.title + " filmi 'İzlenen Filmler' listesinden çıkarıldı."
		messages.add_message(request, messages.SUCCESS, message)
		watchLaters = member.watchLater.all()
	recommend(request)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#Suggesting movies by the system
def recommend(request):

	member = Member.objects.filter(user=request.user).first()
	watchedMovies = member.watchedMovie.all()
	watchLaters = member.watchLater.all()
	recommendedMovies = member.recommendedMovie.all()

	userMovieDetail = []

	for watchLater in watchLaters:
		for director in watchLater.director.all():
			userMovieDetail.append(director)

		for actor in watchLater.cast.all():
			userMovieDetail.append(actor)

		for genre in watchLater.genre.all():
			userMovieDetail.append(genre)

	for watchedMovie in watchedMovies:
		for director in watchedMovie.director.all():
			userMovieDetail.append(director)

		for actor in watchedMovie.cast.all():
			userMovieDetail.append(actor)

		for genre in watchedMovie.genre.all():
			userMovieDetail.append(genre)

	for mov in Movie.objects.all():
		movieDetail = []

		if mov not in watchLaters and mov not in watchedMovies and mov not in recommendedMovies:

			for director in mov.director.all():
				movieDetail.append(director)

			for actor in mov.cast.all():
				movieDetail.append(actor)

			for genre in mov.genre.all():
				movieDetail.append(genre)

			jaccardCount = jaccard(userMovieDetail, movieDetail)
			
			if (len(watchLaters) + len(watchedMovies)) < 5:
				if jaccardCount > 0.24:
					member.recommendedMovie.add(mov)
			elif (len(watchLaters) + len(watchedMovies)) < 10:
				if jaccardCount > 0.10:
					member.recommendedMovie.add(mov)
			else:
				if jaccardCount > 0.07:
					member.recommendedMovie.add(mov)

def jaccard(list1, list2):
    intersection = len(list(set(list1) & set(list2)))
    union = (len(list1 + list2)) - intersection
    return (float(intersection) / union)