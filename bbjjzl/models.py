from __future__ import unicode_literals
from django.db import models
import json

class music(models.Model):
    name = models.CharField(max_length = 140)
    artist = models.CharField(max_length = 140)
    vHash = models.CharField(max_length = 1000)

    def __str__(self):
        return self.name

class musiclist(models.Model):
    uid = models.IntegerField(default = 0)
    songList = models.TextField()

    def __str__(self):
        return self.songList

class mymusic(models.Model):
    uid = models.IntegerField(default = 0)
    songList = models.TextField()

    def __str__(self):
        return self.songList   

class group(models.Model):
    name = models.CharField(max_length = 140)
    uid = models.IntegerField(default = 0)
    proPic = models.CharField(max_length = 1000)
    description = models.TextField()
    songList = models.TextField()
    commentList = models.TextField(default = '[]')

    def __str__(self):
        return self.name

class grouplist(models.Model):
    uid = models.IntegerField(default = 0)
    groupList = models.TextField(default = '[]')

    def __str__(self):
        return self.groupList

class mygroup(models.Model):
    uid = models.IntegerField(default = 0)
    groupList = models.TextField(default = '[]')

    def __str__(self):
        return self.groupList
