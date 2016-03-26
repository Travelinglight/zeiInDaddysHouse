from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^users', views.users, name='users'),
    url(r'^user/new', views.user_new, name='register'),
    url(r'^user/login', views.user_login, name='login'),
    url(r'^group/new$', views.group_new, name='newGroup'),
    url(r'^group/home$', views.group_home, name='newGroup'),
    url(r'^group/upload$', views.group_upload, name='newGroup'),
]
