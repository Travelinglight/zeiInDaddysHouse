from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User

def index(request):
    return render(request, 'bbjjzl/index.html')

def users(request):
    data = User.objects.raw('select * from auth_user;')
    return HttpResponse(data)
