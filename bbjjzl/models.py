from __future__ import unicode_literals
from django.db import models
import json

class musicList(models.Model):
    uid = models.IntegerField(default = 0)
    nSong = models.IntegerField(default = 0)
    songList = models.TextField()

    def __str__(self):
        return self.songList

class music(models.Model):
    name = models.CharField(max_length = 140)
    artist = models.CharField(max_length = 140)
    vHash = models.CharField(max_length = 1000)

    def __str__(self):
        return self.name

class group(models.Model):
    name = models.CharField(max_length = 140)
    uid = models.IntegerField(default = 0)
    proPic = models.CharField(max_length = 1000)
    description = models.TextField()
    nSong = models.IntegerField(default = 0)
    songList = models.TextField()
    nComment = models.IntegerField(default = 0)
    commentList = models.TextField(default = '[]')

    def __str__(self):
        return self.name
