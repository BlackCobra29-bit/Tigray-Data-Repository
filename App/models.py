import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AdminPic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="adminpic")
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile Picture"


class RepositoryGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-id"]

class RepositoryItem(models.Model):
    repository = models.ForeignKey(RepositoryGroup, on_delete=models.CASCADE, related_name='repositories')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="repositories_items/")
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-id"]

class InitiativesModel(models.Model):
    InitiativeName = models.CharField(max_length=255)
    FoundationYear = models.IntegerField()
    InitiativeType = models.CharField(max_length=255)
    InitiativeOrigin = models.CharField(max_length=255)
    AriaOfFocus = models.CharField(max_length=255)
    OfficialLink = models.URLField(max_length=255)

    def __str__(self):
        return self.InitiativeName
    
    class Meta:
        ordering = ["-id"]
