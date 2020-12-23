from django.urls import path
from . import views

urlpatterns = [
	path('', views.user_page, name='user_page'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('password/', views.changePassword, name='changePassword'),
    path('update/', views.updateInfo, name='updateInfo'),
    path('<int:pk>/', views.user_detail, name='user_detail'),
    path('<int:pk>/follow', views.follow, name='follow'),
    path('<int:pk>/removeFollower', views.removeFollower, name='removeFollower'),
    path('notifications/', views.notificationsPage, name='notifications'),
    path('notifications/read/<int:pk>/', views.readNotification, name='read_notification'),
    path('notifications/unread/<int:pk>/', views.unreadNotification, name='unread_notification'),
    path('notifications/delete/<int:pk>/', views.deleteNotification, name='delete_notification'),
]