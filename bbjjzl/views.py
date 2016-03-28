from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import connection
from django.core import serializers
from bbjjzl.models import group as Group
import base64
import hashlib
import os

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

def group_new(request) :
    if request.method == "POST":
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO bbjjzl_group (name, uid, proPic, description, nSong, songList) VALUES('" + request.POST["name"] + "', " + str(request.session["id"]) + ", '" + request.POST["proPic"] + "', '" + request.POST["description"] + "', 0, '[]');")
        except:
            return HttpResponse("Creating group failed!")
        finally:
            cursor.close()
            return HttpResponse("Creating group succeeded!")

    return render(request, 'bbjjzl/group_new.html')

def group_home(request) :
    return render(request, 'bbjjzl/group_home.html')

def file_upload(request) :
    if request.method == "POST":
        """ database select and insert example

        cursor = connection.cursor()
        cursor.execute("INSERT INTO bbjjzl_group (name, uid, proPic, description, nSong, songList) VALUES('Country', 1, 'c0ac2df0e46421292fefbac2b7b91315c07e19a8', 'haha', 0, '[]');")
        result = Group.objects.filter(name = 'Country')
        data = serializers.serialize('json', result)
        return JsonResponse(data, safe=False)
        """

        # base64 decode
        if request.POST['file'].index(','):
            filedata = base64.b64decode(request.POST['file'][request.POST['file'].index(',') + 1:])
        else:
            filedata = base64.b64decode(request.POST['file'])

        # get hash value
        filehash = hashfile(filedata)

        # create the folder if it doesn't exist.
        filepath = settings.BASE_DIR + '/bbjjzl/static/uploads/' + filehash[:2]
        try:
            os.mkdir(filepath)
        except:
            pass

        filepath = filepath + '/' + filehash[2:4]
        try:
            os.mkdir(filepath)
        except:
            pass

        # write file to disk
        fout = open(filepath + '/' + filehash[4:], 'wb')
        try:
            fout.write(filedata)
            fout.close()
            return JsonResponse({'status': 0, 'hash': filehash})
        except:
            return JsonResponse({'status': 1, 'message': 'image saving failed'})
    else:
        return render(request, 'bbjjzl/upload.html')

def hashfile(f):
    sha1 = hashlib.sha1()

    sha1.update(f)

    return sha1.hexdigest()

