from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^new$', views.user_new, name='index'),
]
