import os
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

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

class RepositoryGroup(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="Enter a unique name for the repository group.")
    description = models.TextField(blank=True, null=True, help_text="Provide a brief description of the repository group (optional).")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Repository"

class SubFolder(models.Model):
    parent = models.ForeignKey(
        RepositoryGroup,
        on_delete=models.CASCADE,
        related_name='subfolders',
        help_text="Select the parent folder (Repository Group) that this sub-folder belongs to."
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Enter a unique name for the sub-folder."
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Provide a brief description of the sub-folder (optional)."
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Repository Folders"

class RepositoryItem(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    parent = GenericForeignKey('content_type', 'object_id')
    file = models.FileField(upload_to='repository_items/', validators=[validate_file_type])
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.file.name

    def get_download_count(self):
        """Get the download count for this item"""
        try:
            return self.download_counter.download_count
        except DownloadCounter.DoesNotExist:
            return 0

    class Meta:
        ordering = ["id"]
        verbose_name_plural = "Repository Datasets"

class DownloadCounter(models.Model):
    repository_item = models.OneToOneField(
        RepositoryItem, 
        on_delete=models.CASCADE, 
        related_name='download_counter',
        help_text="The repository item being tracked for downloads."
    )
    download_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this file has been downloaded."
    )
    first_downloaded_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp of the first download."
    )
    last_downloaded_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp of the most recent download."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Downloads for {self.repository_item.title}: {self.download_count}"

    def increment_download(self):
        """Increment the download count and update timestamps"""
        self.download_count += 1
        now = timezone.now()
        
        if not self.first_downloaded_at:
            self.first_downloaded_at = now
        
        self.last_downloaded_at = now
        self.save()

    class Meta:
        ordering = ["-download_count", "-last_downloaded_at"]
        verbose_name_plural = "Download Counters"
        
class ViewCounter(models.Model):
    repository_item = models.OneToOneField(
        RepositoryItem, 
        on_delete=models.CASCADE, 
        related_name='view_counter',
        help_text="The repository item being tracked for views."
    )
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this file has been viewed."
    )
    first_viewed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp of the first view."
    )
    last_viewed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp of the most recent view."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Views for {self.repository_item.title}: {self.view_count}"

    def increment_view(self):
        """Increment the view count and update timestamps"""
        self.view_count += 1
        now = timezone.now()
        
        if not self.first_viewed_at:
            self.first_viewed_at = now
        
        self.last_viewed_at = now
        self.save()

    class Meta:
        ordering = ["-view_count", "-last_viewed_at"]
        verbose_name_plural = "View Counters"

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
    InitiativeTypeforgraph = models.CharField(max_length=255, null=True, blank=True)
    InitiativeOrigin = models.CharField(max_length=255, choices=INITIATIVE_ORIGIN_CHOICES)
    AriaOfFocus = models.TextField()
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
    content = models.TextField()
    DatePublished = models.DateField(default=timezone.now)
    article_type = models.CharField(max_length=20, choices=ARTICLE_TYPES, default='article')

    def __str__(self):
        return self.ArticleTitle

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "TDR Journals"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.ArticleTitle)
            counter = 1
            while Blog.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)