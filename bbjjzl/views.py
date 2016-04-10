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
from bbjjzl.models import music as Music
from bbjjzl.models import musicList as Starred
import base64
import hashlib
import os
import json

def index(request):
    return render(request, 'bbjjzl/index.html')

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
                uid = User.objects.values("id").filter(username = request.POST['username'])[0]["id"]

                try:
                    cursor = connection.cursor()
                    cursor.execute("INSERT INTO bbjjzl_musiclist(uid, nSong, songList) VALUES(" + str(uid) + ", 0, '[]');")
                except:
                    return JsonResponse({'status': 3, 'message': 'music list creation failed!'})
                finally:
                    cursor.close()
                    return JsonResponse({'status': 0, 'message': 'Creating user succeeded!'})

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

def home(request): 
    if not 'id' in request.session.keys():
        return HttpResponse('You must login first')

    username = User.objects.values("username").filter(id = request.session["id"])[0]["username"]
    return render(request, 'bbjjzl/home.html', {'username': username})

def myAccount(request):
    if not 'id' in request.session.keys():
        return HttpResponse('You must login first')

    username = User.objects.values("username").filter(id = request.session["id"])[0]["username"]
    return render(request, 'bbjjzl/my_account.html', {'username': username})

def myPlaylist(request):
    if not 'id' in request.session.keys():
        return HttpResponse('You must login first')

    username = User.objects.values("username").filter(id = request.session["id"])[0]["username"]
    return render(request, 'bbjjzl/my_playlist.html', {'username': username})

def favoriteGroup(request):
    if not 'id' in request.session.keys():
        return HttpResponse('You must login first')

    username = User.objects.values("username").filter(id = request.session["id"])[0]["username"]
    return render(request, 'bbjjzl/favorite_group.html', {'username': username})

def group_new(request) :
    username = User.objects.values("username").filter(id = request.session["id"])[0]["username"]

    if request.method == "POST":
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO bbjjzl_group(name, uid, proPic, description, nSong, songList, nComment, commentList) VALUES('" + request.POST["name"] + "', " + str(request.session["id"]) + ", '" + request.POST["proPic"] + "', '" + request.POST["description"] + "', 0, '[]', 0, '[]');")
        except:
            return JsonResponse({'status': 1, 'message': 'Creating group failed!'})
        finally:
            cursor.close()
            gid = Group.objects.values("id").filter(name = request.POST["name"], uid = request.session["id"])[0]["id"]
            return JsonResponse({'status': 0, 'message': 'Creating group succeeded!'})

    return render(request, 'bbjjzl/group_new.html', {'username': username})

def group_home(request) :
    if not 'id' in request.session.keys():
        return HttpResponse('You must login first')
    username = User.objects.values("username").filter(id = request.session["id"])[0]["username"]
    oriSongList = json.loads(Group.objects.values("songList").filter(id = request.GET.get('gid', 0))[0]["songList"])
    commentList = Group.objects.values("commentList").filter(id = request.GET.get('gid', 0))[0]["commentList"]
    theGroup = Group.objects.values("id", "uid", "name", "description", "proPic").filter(id = request.GET.get('gid', 0))[0]
    idFounder = theGroup["uid"]
    Founder = User.objects.values("username").filter(id = idFounder)[0]["username"]
    likeList = json.loads(Starred.objects.values("songList").filter(uid = request.session["id"])[0]["songList"])

    songList = []
    song = {}
    for i in range(len(oriSongList)):
        theSong = Music.objects.values("name", "artist", "vHash").filter(id = oriSongList[i]["sid"])[0]
        theUser = User.objects.values("username").filter(id = oriSongList[i]["uid"])[0]
        song["id"] = oriSongList[i]["sid"]
        song["name"] = theSong["name"]
        song["artist"] = theSong["artist"]
        song["path"] = "uploads/" + theSong["vHash"][0:2] + "/" + theSong["vHash"][2:4] + "/" + theSong["vHash"][4:]
        song["uploader"] = theUser["username"]
        song["own"] = request.session["id"] == oriSongList[i]["uid"]
        song["like"] = False;
        for j in likeList:
            if int(j) == int(song["id"]):
                song["like"] = True;
        songList.append(song)
        song = {}

    theGroup["proPic"] = "/uploads/" + theGroup["proPic"][0:2] + "/" + theGroup["proPic"][2:4] + "/" + theGroup["proPic"][4:]
    return render(request, 'bbjjzl/group_home.html', {"username":username,"group": theGroup, "songList": songList, "commentList": commentList, "Founder": Founder, "own": idFounder == request.session["id"]})

def upload(request):
    if request.method == "POST":
        if not 'id' in request.session.keys():
            return JsonResponse({'status': 1, 'message': 'You must login first before you upload music'})

        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO bbjjzl_music(name, artist, vHash) VALUES('" + request.POST["name"] + "', '" + request.POST["artist"] + "', '" + request.POST["vHash"] + "');")
        except:
            return JsonResponse({'status': 2, 'message': 'Creating music failed!'})
        finally:
            cursor.close()

        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE bbjjzl_group set nSong = nSong + 1 where id = " + request.POST["gid"] + ";")
        except:
            return JsonResponse({'status': 3, 'message': 'Updating the number of songs failed!'})
        finally:
            cursor.close()

        idSong = Music.objects.values("id").filter(vHash = request.POST["vHash"])[0]["id"]
        songList = Group.objects.values("songList").filter(id = request.POST["gid"])[0]["songList"]
        songList_json = json.loads(songList)
        songList_json.append({"sid": idSong, "uid": request.session["id"]})
        songList = json.dumps(songList_json)
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE bbjjzl_group set songList = '" + songList + "' where id = " + request.POST["gid"] + ";")
        except:
            return JsonResponse({'status': 4, 'message': 'Updating song list failed!'})
        finally:
            cursor.close()

        return JsonResponse({'status': 0, 'message': '1 song added', 'url': '/group/home/?gid=' + str(request.POST["gid"])})
    else:
        if not 'id' in request.session.keys():
            return HttpResponse('You must login first')

        username = User.objects.values("username").filter(id = request.session["id"])[0]["username"]
        groupname = Group.objects.values("name").filter(id = request.GET.get('gid', 0))[0]["name"]
        return render(request, 'bbjjzl/upload.html', {'gid': request.GET.get('gid', 0), 'groupname': groupname, 'username': username})


def file_upload(request) :
    if request.method == "POST":
        """database select and insert example
        instance = Group.objects.values('name').filter(name = 'Jericho')
        return JsonResponse(instance[0], safe=False)"""

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

def hashfile(f):
    sha1 = hashlib.sha1()
    sha1.update(f)
    return sha1.hexdigest()

def delete_from_group(request):
    if request.method == "POST":
        if not 'id' in request.session.keys():
            return JsonResponse({'status': 1, 'message': 'You must login first to delete the music'})

        songList = Group.objects.values("songList").filter(id = request.POST["gid"])[0]["songList"]
        songList_json = json.loads(songList)

        print(songList_json)
        for i in range(len(songList_json)):
            print(i)
            print(songList_json[i])
            print(songList_json)
            if int(songList_json[i]["sid"]) == int(request.POST["sid"]):
                if int(songList_json[i]["uid"]) != int(request.session["id"]):
                    return JsonResponse({'status': 2, 'message': 'Deletion request denied'})
                else:
                    songList_json.pop(i)
                    break

        songList = json.dumps(songList_json)
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE bbjjzl_group set songList = '" + songList + "' where id = " + request.POST["gid"] + ";")
        except:
            return JsonResponse({'status': 4, 'message': 'Updating song list failed!'})
        finally:
            cursor.close()

        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE bbjjzl_group set nSong = nSong - 1 where id = " + request.POST["gid"] + ";")
        except:
            return JsonResponse({'status': 3, 'message': 'Updating the number of songs failed!'})
        finally:
            cursor.close()

        return JsonResponse({'status': 0, 'message': 'music deleted'})

def like_song(request):
    if request.method == "POST":
        if not 'id' in request.session.keys():
            return JsonResponse({'status': 1, 'message': 'You must login first to delete the music'})

        songList = json.loads(Starred.objects.values("songList").filter(id = request.session["id"])[0]["songList"])
        for i in songList:
            if int(i) == request.POST["sid"]:
                return JsonResponse({'status': 0, 'message': 'song liked'})
        songList.append(request.POST["sid"])
        songList = json.dumps(songList)
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE bbjjzl_musiclist set songList = '" + songList + "' where id = " + request.session["id"] + ";")
        except:
            return JsonResponse({'status': 2, 'message': 'Updating starred song list failed!'})
        finally:
            cursor.close()
        return JsonResponse({'status': 0, 'message': 'song liked'})

def dislike_song(request):
    if request.method == "POST":
        if not 'id' in request.session.keys():
            return JsonResponse({'status': 1, 'message': 'You must login first to delete the music'})

        songList = json.loads(Starred.objects.values("songList").filter(id = request.session["id"])[0]["songList"])
        for i in songList:
            if int(i) == request.POST["sid"]:
                return JsonResponse({'status': 0, 'message': 'song liked'})
        songList.append(request.POST["sid"])
        songList = json.dumps(songList)
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE bbjjzl_musiclist set songList = '" + songList + "' where id = " + request.session["id"] + ";")
        except:
            return JsonResponse({'status': 2, 'message': 'Updating starred song list failed!'})
        finally:
            cursor.close()
        return JsonResponse({'status': 0, 'message': 'song liked'})
