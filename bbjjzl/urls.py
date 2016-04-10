from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^user/new', views.user_new, name='register'),
    url(r'^user/login', views.user_login, name='login'),
    url(r'^group/new$', views.group_new, name='newGroup'),
    url(r'^group/home/', views.group_home, name='homeGroup'),
    url(r'^upload', views.upload, name='upload'),
    url(r'^fileupload$', views.file_upload, name='upload'),
    url(r'^home$', views.home, name="home"),
    url(r'^myAccount$', views.myAccount, name="myAccount"),
    url(r'^myPlaylist$', views.myPlaylist, name="myPlaylist"),
    url(r'^favoriteGroup$', views.favoriteGroup, name="favoriteGroup"),
]
