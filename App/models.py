import os
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone

class AdminPic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='adminpic')
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile Picture"
    
class RepositoryGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']

def validate_zip_file(value):
    if not value.name.endswith('.zip'):
        raise ValidationError("Only zip files are allowed.")

class Repository(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the repository")
    description = models.TextField(blank=True, help_text="Description of the repository")
    uploaded_at = models.DateTimeField(default=timezone.now, help_text="Date and time when the repository was uploaded")
    zip_file = models.FileField(upload_to='repositories/', validators=[validate_zip_file], help_text="Upload the repository folder as a zip file")

    def __str__(self):
        return self.name

    def filename(self):
        return os.path.basename(self.zip_file.name)

    class Meta:
        verbose_name = "Repository"
        verbose_name_plural = "Repositories"
