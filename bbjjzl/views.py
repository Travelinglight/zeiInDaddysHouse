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
from bbjjzl.models import musiclist as Musiclist
from bbjjzl.models import grouplist as Grouplist
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
                    cursor.execute("INSERT INTO bbjjzl_musiclist(uid, songList) VALUES(" + str(uid) + ", '[]');")
                    cursor.execute("INSERT INTO bbjjzl_grouplist(uid, groupList) VALUES(" + str(uid) + ", '[]');")
                except:
                    return JsonResponse({'status': 3, 'message': 'user initialiation failed'})
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

    oriSongs = Music.objects.values("id", "name", "artist", "vHash", "gid").filter(uid = request.session["id"])
    likeList = json.loads(Musiclist.objects.values("songList").filter(uid = request.session["id"])[0]["songList"])
    username = User.objects.values("username").filter(id = request.session["id"])[0]["username"]
    songList = []
    song = {}
    for i in range(len(oriSongs)):
        theGroup = Group.objects.values("name").filter(id = oriSongs[i]["gid"])[0]
        song["id"] = oriSongs[i]["id"]
        song["name"] = oriSongs[i]["name"]
        song["artist"] = oriSongs[i]["artist"]
        song["path"] = "uploads/" + oriSongs[i]["vHash"][0:2] + "/" + oriSongs[i]["vHash"][2:4] + "/" + oriSongs[i]["vHash"][4:]
        song["group"] = theGroup["name"]
        song["like"] = False;
        for j in likeList:
            if int(j) == int(song["id"]):
                song["like"] = True;
        songList.append(song)
        song = {}

    groupList = Group.objects.values("id", "name", "proPic", "description").filter(uid = request.session["id"])
    for i in range(len(groupList)):
        groupList[i]["proPic"] = "uploads/" + groupList[i]["proPic"][0:2] + "/" + groupList[i]["proPic"][2:4] + "/" + groupList[i]["proPic"][4:]
        groupList[i]["Founder"] = username

    return render(request, 'bbjjzl/my_account.html', {'username': username, 'songList': songList, 'groupList': groupList})

def myPlaylist(request):
    if not 'id' in request.session.keys():
        return HttpResponse('You must login first')

    likeList = json.loads(Musiclist.objects.values("songList").filter(uid = request.session["id"])[0]["songList"])
    songList = []
    song = {}
    for i in range(len(likeList)):
        theSong = Music.objects.values("id", "name", "artist", "vHash", "gid", "uid").filter(id = int(likeList[i]))[0]
        theGroup = Group.objects.values("name").filter(id = theSong["gid"])[0]
        song["id"] = theSong["id"]
        song["name"] = theSong["name"]
        song["artist"] = theSong["artist"]
        song["path"] = "uploads/" + theSong["vHash"][0:2] + "/" + theSong["vHash"][2:4] + "/" + theSong["vHash"][4:]
        song["group"] = theGroup["name"]
        song["like"] = True;
        song["own"] = theSong["uid"] == request.session["id"]
        songList.append(song)
        song = {}
    username = User.objects.values("username").filter(id = request.session["id"])[0]["username"]
    return render(request, 'bbjjzl/my_playlist.html', {'username': username, 'songList': songList})

def favoriteGroup(request):
    if not 'id' in request.session.keys():
        return HttpResponse('You must login first')

    username = User.objects.values("username").filter(id = request.session["id"])[0]["username"]
    return render(request, 'bbjjzl/favorite_group.html', {'username': username})

def group_new(request) :
    if request.method == "POST":
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO bbjjzl_group(name, uid, proPic, description, commentList) VALUES('" + request.POST["name"] + "', " + str(request.session["id"]) + ", '" + request.POST["proPic"] + "', '" + request.POST["description"] + "', '[]');")
        except:
            return JsonResponse({'status': 1, 'message': 'Creating group failed!'})
        finally:
            cursor.close()
            gid = Group.objects.values("id").filter(name = request.POST["name"], uid = request.session["id"])[0]["id"]
            return JsonResponse({'status': 0, 'message': 'Creating group succeeded!', 'url': '/group/home/?gid=' + str(gid)})
    else:
        username = User.objects.values("username").filter(id = request.session["id"])[0]["username"]
        return render(request, 'bbjjzl/group_new.html', {'username': username})

def group_home(request) :
    if not 'id' in request.session.keys():
        return HttpResponse('You must login first')
    username = User.objects.values("username").filter(id = request.session["id"])[0]["username"]
    oriSongList = Music.objects.values("id", "name", "artist", "vHash", "gid", "uid").filter(gid = request.GET.get('gid', 0))
    commentList = json.loads(Group.objects.values("commentList").filter(id = request.GET.get('gid', 0))[0]["commentList"])
    theGroup = Group.objects.values("id", "uid", "name", "description", "proPic").filter(id = request.GET.get('gid', 0))[0]
    idFounder = theGroup["uid"]
    Founder = User.objects.values("username").filter(id = idFounder)[0]["username"]
    likeList = json.loads(Musiclist.objects.values("songList").filter(uid = request.session["id"])[0]["songList"])
    likeGrouplist = json.loads(Grouplist.objects.values("groupList").filter(uid = request.session["id"])[0]["groupList"])

    songList = []
    song = {}
    for i in range(len(oriSongList)):
        theUser = User.objects.values("username").filter(id = oriSongList[i]["uid"])[0]
        song["id"] = oriSongList[i]["id"]
        song["name"] = oriSongList[i]["name"]
        song["artist"] = oriSongList[i]["artist"]
        song["path"] = "uploads/" + oriSongList[i]["vHash"][0:2] + "/" + oriSongList[i]["vHash"][2:4] + "/" + oriSongList[i]["vHash"][4:]
        song["uploader"] = theUser["username"]
        song["own"] = request.session["id"] == oriSongList[i]["uid"]
        song["like"] = False;
        for j in likeList:
            if int(j) == int(song["id"]):
                song["like"] = True;
        songList.append(song)
        song = {}

    theGroup["like"] = False;
    for i in likeGrouplist:
        if int(i) == int(request.GET.get('gid', 0)):
            theGroup["like"] = True;

    theGroup["proPic"] = "/uploads/" + theGroup["proPic"][0:2] + "/" + theGroup["proPic"][2:4] + "/" + theGroup["proPic"][4:]
    return render(request, 'bbjjzl/group_home.html', {"username":username,"group": theGroup, "songList": songList, "commentList": commentList, "Founder": Founder, "own": idFounder == request.session["id"]})

def upload(request):
    if request.method == "POST":
        if not 'id' in request.session.keys():
            return JsonResponse({'status': 1, 'message': 'You must login first before you upload music'})

        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO bbjjzl_music(name, artist, vHash, gid, uid) VALUES('" + request.POST["name"] + "', '" + request.POST["artist"] + "', '" + request.POST["vHash"] + "', " + str(request.POST["gid"]) + ", " + str(request.session["id"]) + ");")
        except:
            return JsonResponse({'status': 2, 'message': 'Creating music failed!'})
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

        uid = Music.objects.values("uid").filter(id = request.POST["sid"])[0]["uid"]
        if uid != request.session["id"]:
            return JsonResponse({'status': 2, 'message': 'You hvae no previlege to delete this song'})

        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM bbjjzl_music where id = " + request.POST["sid"] + ";")
        except:
            return JsonResponse({'status': 3, 'message': 'Unable to delete the song'})
        finally:
            cursor.close()

        return JsonResponse({'status': 0, 'message': 'successfully deleted the song'})

def like_song(request):
    if request.method == "POST":
        if not 'id' in request.session.keys():
            return JsonResponse({'status': 1, 'message': 'You must login first to like the music'})

        songList = json.loads(Musiclist.objects.values("songList").filter(uid = request.session["id"])[0]["songList"])
        for i in songList:
            if int(i) == int(request.POST["sid"]):
                return JsonResponse({'status': 0, 'message': 'song liked'})
        songList.append(str(request.POST["sid"]))
        songList = json.dumps(songList)
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE bbjjzl_musiclist set songList = '" + songList + "' where uid = " + str(request.session["id"]) + ";")
        except:
            return JsonResponse({'status': 2, 'message': 'Updating starred song list failed!'})
        finally:
            cursor.close()

        return JsonResponse({'status': 0, 'message': 'song liked'})

def dislike_song(request):
    if request.method == "POST":
        if not 'id' in request.session.keys():
            return JsonResponse({'status': 1, 'message': 'You must login first to dislike the music'})

        songList = json.loads(Musiclist.objects.values("songList").filter(uid = request.session["id"])[0]["songList"])

        for index, item in enumerate(songList):
            if int(item) == int(request.POST["sid"]):
                songList.pop(index)
                songList = json.dumps(songList)
                try:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE bbjjzl_musiclist set songList = '" + songList + "' where uid = " + str(request.session["id"]) + ";")
                except:
                    return JsonResponse({'status': 2, 'message': 'Updating starred song list failed!'})
                finally:
                    cursor.close()

                return JsonResponse({'status': 0, 'message': 'song disliked'})

        return JsonResponse({'status': 4, 'message': 'song not in like list'})

def group_comment(request):
    if request.method == "POST":
        if not 'id' in request.session.keys():
            return JsonResponse({'status': 1, 'message': 'You must login first to comment the group'})

        username = User.objects.values("username").filter(id = request.session["id"])[0]["username"]
        commentList = json.loads(Group.objects.values("commentList").filter(id = request.POST["gid"])[0]["commentList"])
        commentList.append({"content": request.POST["content"], "username": username, "uid": request.session["id"]})
        commentList = json.dumps(commentList)
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE bbjjzl_group set commentList = '" + commentList + "' where id = " + request.POST["gid"] + ";")
        except:
            return JsonResponse({'status': 4, 'message': 'Updating song list failed!'})
        finally:
            cursor.close()

        return JsonResponse({'status': 0, 'message': 'comment added'})

def like_group(request):
    if request.method == "POST":
        if not 'id' in request.session.keys():
            return JsonResponse({'status': 1, 'message': 'You must login first to like the music'})

        groupList = json.loads(Grouplist.objects.values("groupList").filter(uid = request.session["id"])[0]["groupList"])
        for i in groupList:
            if int(i) == int(request.POST["gid"]):
                return JsonResponse({'status': 0, 'message': 'group liked'})
        groupList.append(str(request.POST["gid"]))
        groupList = json.dumps(groupList)
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE bbjjzl_grouplist set groupList = '" + groupList + "' where uid = " + str(request.session["id"]) + ";")
        except:
            return JsonResponse({'status': 2, 'message': 'Updating starred group list failed!'})
        finally:
            cursor.close()

        return JsonResponse({'status': 0, 'message': 'group liked'})

def dislike_group(request):
    if request.method == "POST":
        if not 'id' in request.session.keys():
            return JsonResponse({'status': 1, 'message': 'You must login first to dislike the music'})

        groupList = json.loads(Grouplist.objects.values("groupList").filter(uid = request.session["id"])[0]["groupList"])

        for index, item in enumerate(groupList):
            if int(item) == int(request.POST["gid"]):
                groupList.pop(index)
                groupList = json.dumps(groupList)
                try:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE bbjjzl_grouplist set groupList = '" + groupList + "' where uid = " + str(request.session["id"]) + ";")
                except:
                    return JsonResponse({'status': 2, 'message': 'Updating starred group list failed!'})
                finally:
                    cursor.close()

                return JsonResponse({'status': 0, 'message': 'group disliked'})

        return JsonResponse({'status': 4, 'message': 'group not in like list'})

def group_dismiss(request):
    if request.method == "POST":
        if not 'id' in request.session.keys():
            return JsonResponse({'status': 1, 'message': 'You must login first if you want to dismiss this group'})

        idFounder = Group.objects.values("uid").filter(id = request.POST["gid"])[0]["uid"]
        if not idFounder == request.session["id"]:
            return JsonResponse({'status': 2, 'message': 'You have no permission to do this'})

        try:
            cursor = connection.cursor()
            cursor.execute("DELETE from bbjjzl_group where id = " + str(request.POST["gid"]) + ";")
        except:
            return JsonResponse({'status': 2, 'message': 'Updating starred group list failed!'})
        finally:
            cursor.close()

        return JsonResponse({'status': 0, 'message': 'group dismissed'})
