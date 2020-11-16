from django.shortcuts import render, get_object_or_404
from .models import Actor, Director, Genre, Movie

import os.path


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

	return render(request, "movieApp/index.html", {"movies": movies})

def movie_detail(request, pk):
	movie = get_object_or_404(Movie, pk=pk)

	return render(request, "movieApp/movie_detail.html", {"movie":movie})

# Actor's movies
def actorMovies(request, pk):
	filtered = get_object_or_404(Actor, pk=pk)
	movies = Movie.objects.filter(cast__pk=pk)

	return render(request, "movieApp/filtered_page.html", {"filtered":filtered, "movies": movies})

# Director's movies
def directorMovies(request, pk):
	filtered = get_object_or_404(Director, pk=pk)
	movies = Movie.objects.filter(director__pk=pk)

	return render(request, "movieApp/filtered_page.html", {"filtered": filtered, "movies": movies})

# Movies by genre
def genreMovies(request, pk):
	filtered = get_object_or_404(Genre, pk=pk)
	movies = Movie.objects.filter(genre__pk=pk)

	return render(request, "movieApp/filtered_page.html", {"filtered": filtered, "movies": movies})

