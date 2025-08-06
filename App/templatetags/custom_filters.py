from django import template
from django.utils.html import strip_tags
import os
import re

register = template.Library()

EXCEL_EXTENSIONS = {'.xls', '.xlsx', '.xlsm', '.xlsb', '.csv'}

@register.filter
def basename(value):
    
    return os.path.basename(value)

@register.filter
def read_more_content(value):
    
    return strip_tags(value).strip()[:150]

@register.filter    
def get_file_icon(file_name):
    """
    Return appropriate icon class and color based on file extension
    """
    if not file_name:
        return {'icon': 'fa fa-file', 'color': '#666'}
    
    file_extension = file_name.lower().split('.')[-1] if '.' in file_name else ''
    
    # Microsoft Office files
    if file_extension in ['xlsx', 'xls']:
        return {'icon': 'fa fa-file-excel', 'color': '#217346'}  # Excel green
    elif file_extension in ['docx', 'doc']:
        return {'icon': 'fa fa-file-word', 'color': '#0d6efd'}  # Word blue
    elif file_extension in ['pptx', 'ppt']:
        return {'icon': 'fa fa-file-powerpoint', 'color': '#d63384'}  # PowerPoint pink
    elif file_extension == 'pdf':
        return {'icon': 'fa fa-file-pdf', 'color': '#dc3545'}   # PDF red
    
    # Data and CSV files
    elif file_extension == 'csv':
        return {'icon': 'fa fa-file-csv', 'color': '#198754'}  # CSV green
    elif file_extension in ['json', 'xml']:
        return {'icon': 'fa fa-file-code', 'color': '#fd7e14'}  # Code orange
    
    # Image files
    elif file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp']:
        return {'icon': 'fa fa-file-image', 'color': '#6f42c1'}  # Image purple
    
    # Video files
    elif file_extension in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm']:
        return {'icon': 'fa fa-file-video', 'color': '#e83e8c'}  # Video pink
    
    # Audio files
    elif file_extension in ['mp3', 'wav', 'flac', 'aac', 'ogg']:
        return {'icon': 'fa fa-file-audio', 'color': '#fd7e14'}  # Audio orange
    
    # Archive files
    elif file_extension in ['zip', 'rar', '7z', 'tar', 'gz']:
        return {'icon': 'fa fa-file-archive', 'color': '#6c757d'}  # Archive gray
    
    # Text files
    elif file_extension in ['txt', 'md', 'rtf']:
        return {'icon': 'fa fa-file-text', 'color': '#495057'}  # Text dark gray
    
    # Database files
    elif file_extension in ['db', 'sqlite', 'sql']:
        return {'icon': 'fa fa-database', 'color': '#0dcaf0'}  # Database cyan
    
    # Presentation files
    elif file_extension in ['key', 'odp']:
        return {'icon': 'fa fa-file-powerpoint', 'color': '#d63384'}  # Presentation pink
    
    # Spreadsheet files
    elif file_extension in ['ods', 'numbers']:
        return {'icon': 'fa fa-file-excel', 'color': '#217346'}  # Spreadsheet green
    
    # Document files
    elif file_extension in ['odt', 'pages']:
        return {'icon': 'fa fa-file-word', 'color': '#0d6efd'}  # Document blue
    
    else:
        return {'icon': 'fa fa-file', 'color': '#666'}          # Default 
    
@register.filter
def normalize_readme(value):
    """
    Converts 'README_randomstring.txt' to 'README.txt'
    Only affects files that match the pattern.
    """
    return re.sub(r'^README.*\.txt$', 'README.txt', value)

@register.filter(name='is_excel_file')
def is_excel_file(filename):
    """
    Return True if `filename` has an extension in EXCEL_EXTENSIONS.
    Works if `filename` is a FileField/FilePath or plain string.
    Case-insensitive and safe for filenames without extension or None.
    """
    if not filename:
        return False

    # If given a FileField/File instance, try to get the name attribute
    if hasattr(filename, 'name'):
        filename = filename.name

    # Extract extension and normalize
    _, ext = os.path.splitext(str(filename))
    return ext.lower() in EXCEL_EXTENSIONS

@register.filter
def get_item(dictionary, key):
    """Template filter to get a dictionary item by key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, "")
    return ""