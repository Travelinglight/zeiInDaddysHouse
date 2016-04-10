from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^user/new', views.user_new, name='register'),
    url(r'^user/login', views.user_login, name='login'),
    url(r'^group/new$', views.group_new, name='newGroup'),
    url(r'^group/home/', views.group_home, name='homeGroup'),
    url(r'^group/delete$', views.delete_from_group, name='delete_from_group'),
    url(r'^group/comment$', views.group_comment, name='group_comment'),
    url(r'^upload', views.upload, name='upload'),
    url(r'^fileupload$', views.file_upload, name='upload'),
    url(r'^home$', views.home, name="home"),
    url(r'^myAccount$', views.myAccount, name="myAccount"),
    url(r'^myPlaylist$', views.myPlaylist, name="myPlaylist"),
    url(r'^favoriteGroup$', views.favoriteGroup, name="favoriteGroup"),
    url(r'^likeSong$', views.like_song, name="like_song"),
    url(r'^dislikeSong$', views.dislike_song, name="dislike_song"),
    url(r'^likeGroup$', views.like_group, name="like_group"),
    url(r'^dislikeGroup$', views.dislike_group, name="dislike_group"),
]
