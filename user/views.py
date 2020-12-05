from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required

from notifications.signals import notify

from .models import Member, Relationship

def login(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = auth.authenticate(username=username, password=password)
		if user is not None:
			auth.login(request, user)
			messages.add_message(request, messages.SUCCESS, 'Giriş Başarılı.')
			return redirect('index')
		else:
			messages.add_message(request, messages.ERROR, "Kullanıcı adı veya parola yanlış.")
			return redirect('login')

	else:
		return render(request, 'user/login.html')


def register(request):
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		repassword = request.POST['repassword']

		if User.objects.filter(username = username).exists():
			messages.add_message(request, messages.WARNING, "Bu kullanıcı adı mevcut.")
			return redirect('register')
		else:
			if User.objects.filter(email = email).exists():
				messages.add_message(request, messages.WARNING, "Bu email mevcut")
				return redirect('register')
			else:
				if password != repassword:
					messages.add_message(request, messages.WARNING, "Şifreler aynı değil")
					return redirect('register')
				else:
					if password.isnumeric():
						messages.add_message(request, messages.WARNING, "Şifre sadece numaradan oluşamaz.")
						return redirect('register')
					elif len(password) < 8:
						messages.add_message(request, messages.WARNING, "Şifreniz en az 8 karakter içermelidir.")
						return redirect('register')

					else:
						user = User.objects.create_user(username=username, email=email, password=password)
						user.save()
						auth.login(request, user)
						messages.add_message(request, messages.SUCCESS, 'Hesap oluşturuldu.')
						return redirect('index')
	else:
		return render(request, 'user/register.html')

@login_required
def logout(request):
	if request.method == 'POST':
		auth.logout(request)
		messages.add_message(request, messages.SUCCESS, "Oturumunuz kapatıldı.")
		return redirect('index')

@login_required
def changePassword(request):
	if request.method == 'POST':
		oldPassword = request.POST['oldPassword']
		newPassword = request.POST['newPassword']
		reNewPassword = request.POST['reNewPassword']
		if request.user.check_password(oldPassword):
			if newPassword == reNewPassword:
				request.user.set_password(newPassword)
				request.user.save()
				update_session_auth_hash(request, request.user)
				messages.add_message(request, messages.SUCCESS, "Şifreniz güncellendi.")
				return redirect('index')
			else:
				messages.add_message(request, messages.ERROR, "Şifreler aynı değil.")
				return redirect('changePassword')
		else:
			messages.add_message(request, messages.ERROR, "Eski parola yanlış girilmiş.")
			return redirect('changePassword')
	else:
		return render(request, 'user/change_password.html')

@login_required
def user_page(request):
	member = Member.objects.filter(user=request.user).first()
	if not member:
		member = Member.objects.create(user=request.user)
	watchedMovies = member.watchedMovie.all()
	watchLaters = member.watchLater.all()
	recommendedMovies = Member.objects.filter(user=request.user).first().recommendedMovie.all()
	relation = Relationship.objects.filter(member=member).first()
	followers = []
	followedUsers = []
	if relation:
		followers = relation.follower.all()
		followedUsers = relation.followed.all()
	return render(
		request, "user/user_page.html", {
		"watchedMovies":watchedMovies, "watchLaters":watchLaters, "recommendedMovies": recommendedMovies,"followers": followers, "followedUsers":followedUsers
		})

def user_detail(request, pk):
	if pk == request.user.pk:
		return redirect('user_page')
	member = Member.objects.filter(user__pk=pk).first()
	if not member: 
		user = User.objects.filter(pk=pk).first()
		member = Member.objects.create(user=user)
	watchedMovies = member.watchedMovie.all()
	watchLaters = member.watchLater.all()
	recommendedMovies = member.recommendedMovie.all()
	relation = Relationship.objects.filter(member=member).first()
	followers = []
	followedUsers = []
	userFollowedList = []
	relationRequest = None
	if request.user.is_authenticated:
		requestUser = Member.objects.filter(user=request.user).first()
		relationRequest = Relationship.objects.filter(member = requestUser).first()
	if relationRequest:
		userFollowedList = relationRequest.followed.all()
	if relation:
		followers = relation.follower.all()
		followedUsers = relation.followed.all()
	return render(
		request, "user/user_detail.html", {
		"member": member, "watchedMovies":watchedMovies, "watchLaters":watchLaters, "recommendedMovies": recommendedMovies,"followers": followers, "followedUsers":followedUsers, "userFollowedList": userFollowedList
		})

def follow(request, pk):

	member = Member.objects.filter(user__pk=pk).first()

	user = Member.objects.filter(user=request.user).first()
	requestUser = Relationship.objects.filter(member=user).first()
	followedUser = Relationship.objects.filter(member=member).first()
	person = User.objects.filter(pk=pk).first()

	if not member:
		memberUser = User.objects.filter(pk=pk).first()
		member = Member.objects.create(user=memberUser)
		
	if not user:
		user = Member.objects.create(user=request.user)

	if not requestUser:
		requestUser = Relationship.objects.create(member=user)

	if not followedUser:
		followedUser = Relationship.objects.create(member=member)

	followers = requestUser.follower.all()
	followedUsers = requestUser.followed.all()

	if member not in followedUsers:
		requestUser.followed.add(member)
		followedUser.follower.add(user)
		notify.send(request.user, recipient = person, verb = "sizi takip ediyor.")
		message = person.username + " kişisi takip ediliyor."
		messages.add_message(request, messages.SUCCESS, message)

	else:
		requestUser.followed.remove(member)
		followedUser.follower.remove(user)
		message = person.username + " kişisi takip edilenlerden çıkarıldı."
		messages.add_message(request, messages.ERROR, message)

	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def removeFollower(request, pk):
	member = Member.objects.filter(user__pk=pk).first()
	user = Member.objects.filter(user=request.user).first()
	requestUser = Relationship.objects.filter(member=user).first()
	followedUser = Relationship.objects.filter(member=member).first()
	requestUser.follower.remove(member)
	followedUser.followed.remove(user)
	
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def notificationsPage(request):
	unreadNotifications = request.user.notifications.unread()
	readNotifications = request.user.notifications.read()
	return render(request, "parts/notifications.html", {"unreadNotifications": unreadNotifications, "readNotifications": readNotifications})

def readNotification(request, pk):
	notification = request.user.notifications.filter(pk=pk)
	notification.mark_all_as_read()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def unreadNotification(request, pk):
	notification = request.user.notifications.filter(pk=pk)
	notification.mark_all_as_unread()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def deleteNotification(request, pk):
	notification = request.user.notifications.filter(pk=pk)
	notification.delete()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))