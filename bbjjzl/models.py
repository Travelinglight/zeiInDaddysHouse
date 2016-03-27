from __future__ import unicode_literals
from django.db import models
import json

class musicList(models.Model):
    title = models.CharField(max_length = 140)
    uid = models.IntegerField(default = 0)
    nSong = models.IntegerField(default = 0)
    songList = models.TextField()

    def setSongs(self, x):
        self.songList = json.dumps(x)

    def getSongs(self, x):
        return json.loads(self.foo)

    def __str__(self):
        return self.title

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

    def setSongs(self, x):
        self.songList = json.dumps(x)

    def getSongs(self, x):
        return json.loads(self.foo)

    def __str__(self):
        return self.name
