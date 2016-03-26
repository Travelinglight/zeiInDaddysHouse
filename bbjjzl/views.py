from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def index(request):
    return render(request, 'bbjjzl/index.html')

def users(request):
    data = User.objects.raw('select * from auth_user;')
    print(request.session['id'])
    return HttpResponse(data)

def user_new(request) :
    if request.method == "POST":
        try:
            user = User.objects.get(username=request.POST['username'])
            return JsonResponse({'status': 1})
        except:
            try:
                user = User.objects.get(email=request.POST['email'])
                return JsonResponse({'status': 2})
            except:
                user = User.objects.create_user(username=request.POST['username'],
                                         email=request.POST['email'],
                                         password=request.POST['password'])
                print(user)
                user.save()
                return JsonResponse({'status': 0})

def user_login(request) :
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        request.session['id'] = user.id
        if user.is_active:
            return JsonResponse({'status': 0})
        else:
            return JsonResponse({'status': 1})
    else :
        return JsonResponse({'status': 2})
