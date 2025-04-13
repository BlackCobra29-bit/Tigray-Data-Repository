import os
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from froala_editor.fields import FroalaField
from django.core.exceptions import ValidationError

def validate_file_type(value):
    valid_extensions = [
        # Documents
        '.doc', '.docx', '.pdf', '.txt', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp', '.rtf',
        
        # Images
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp',
        
        # Audio
        '.mp3', '.wav', '.aac', '.ogg', '.flac', '.wma', '.m4a',
        
        # Video
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
        
        # Archives
        '.zip', '.rar', '.tar', '.gz', '.7z', '.bz2',
        
        # Code and Markup
        '.html', '.css', '.js', '.py', '.java', '.c', '.cpp', '.php', '.json', '.xml', '.yml', '.yaml', '.sql', '.sh',
        
        # Miscellaneous
        '.csv', '.md', '.epub', '.ico', '.log', '.dat'
    ]
    
    ext = os.path.splitext(value.name)[1]  # Extract the file extension
    if ext.lower() not in valid_extensions:
        raise ValidationError(f'Unsupported file type. Allowed types are: {", ".join(valid_extensions)}')

class AdminPic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="adminpic")
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile Picture"
    
    class Meta:
        verbose_name_plural = "Admin Pictures"


class RepositoryGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Repository Groups"

class RepositoryItem(models.Model):
    repository = models.ForeignKey(RepositoryGroup, on_delete=models.CASCADE, related_name='repositories')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="repositories_items/", validators=[validate_file_type])
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Respository Datasets"

class InitiativesModel(models.Model):
    
    INITIATIVE_ORIGIN_CHOICES = [
        ('Ethiopia (Outside of Tigray)', 'Ethiopia (Outside of Tigray)'),
        ('Africa', 'Africa'),
        ('North America', 'North America'),
        ('Central/South America', 'Central/South America'),
        ('Asia', 'Asia'),
        ('Europe', 'Europe'),
        ('Middle East', 'Middle East'),
        ('Australia', 'Australia'),
    ]

    InitiativeName = models.CharField(max_length=255)
    FoundationYear = models.DateField()
    InitiativeType = models.CharField(max_length=255)
    InitiativeOrigin = models.CharField(max_length=255, choices=INITIATIVE_ORIGIN_CHOICES)
    AriaOfFocus = models.CharField(max_length=255)
    OfficialLink = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.InitiativeName

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Initiatives & Organizations"
        
class Blog(models.Model):
    ARTICLE_TYPES = [
        ('articles', 'Articles'),
        ('journals', 'Journals'),
        ('special_issues', 'Special Issues'),
    ]
    
    ArticleTitle = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = FroalaField(theme='dark')
    DatePublished = models.DateField(default=timezone.now)
    article_type = models.CharField(max_length=20, choices=ARTICLE_TYPES, default='article')

    def __str__(self):
        return self.ArticleTitle

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Blog Articles"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.ArticleTitle)
            counter = 1
            while Blog.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)