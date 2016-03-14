from django.shortcuts import render
from django.contrib.auth.models import User

def user_new(request) :
    if request.method == "POST":
        user = User.objects.create_user(username=request.data['username'],
                                 email=request.data['email'],
                                 password=request.data['password'])
        user.save()

