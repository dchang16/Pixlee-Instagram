from __future__ import unicode_literals

from django.db import models


# class Name(models.Model):
# 	name = models.CharField(max_length=30,unique=True)

class Item(models.Model):
	type = models.CharField(max_length=30)
	user = models.CharField(max_length=30)
	link = models.CharField(max_length=128)
	url = models.CharField(max_length=255, unique=True)
	tagtime = models.DateTimeField(auto_now_add=True)
	name = models.CharField(max_length=30, default="Pixlee")