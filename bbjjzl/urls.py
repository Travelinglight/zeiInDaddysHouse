from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^user/new', views.user_new, name='register'),
    url(r'^user/login', views.user_login, name='login'),
]
