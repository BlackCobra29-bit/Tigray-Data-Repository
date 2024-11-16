# myapp/templatetags/custom_filters.py
from django import template
import os

register = template.Library()

ICON_MAP = {
    # Text files
    '.txt': 'fa-file-alt',
    '.md': 'fa-file-alt',
    '.rtf': 'fa-file-alt',

    # Document files
    '.pdf': 'fa-file-pdf',
    '.doc': 'fa-file-word',
    '.docx': 'fa-file-word',
    '.odt': 'fa-file-word',

    # Spreadsheet files
    '.xls': 'fa-file-excel',
    '.xlsx': 'fa-file-excel',
    '.csv': 'fa-file-csv',
    '.ods': 'fa-file-excel',

    # Presentation files
    '.ppt': 'fa-file-powerpoint',
    '.pptx': 'fa-file-powerpoint',
    '.odp': 'fa-file-powerpoint',

    # Image files
    '.jpg': 'fa-file-image',
    '.jpeg': 'fa-file-image',
    '.png': 'fa-file-image',
    '.gif': 'fa-file-image',
    '.bmp': 'fa-file-image',
    '.svg': 'fa-file-image',
    '.tiff': 'fa-file-image',

    # Video files
    '.mp4': 'fa-file-video',
    '.mov': 'fa-file-video',
    '.avi': 'fa-file-video',
    '.mkv': 'fa-file-video',
    '.wmv': 'fa-file-video',
    '.flv': 'fa-file-video',

    # Audio files
    '.mp3': 'fa-file-audio',
    '.wav': 'fa-file-audio',
    '.ogg': 'fa-file-audio',
    '.flac': 'fa-file-audio',
    '.aac': 'fa-file-audio',

    # Compressed files
    '.zip': 'fa-file-archive',
    '.rar': 'fa-file-archive',
    '.7z': 'fa-file-archive',
    '.tar': 'fa-file-archive',
    '.gz': 'fa-file-archive',

    # Code files
    '.py': 'fa-file-code',
    '.js': 'fa-file-code',
    '.html': 'fa-file-code',
    '.css': 'fa-file-code',
    '.java': 'fa-file-code',
    '.c': 'fa-file-code',
    '.cpp': 'fa-file-code',
    '.php': 'fa-file-code',
    '.rb': 'fa-file-code',
    '.xml': 'fa-file-code',
    '.json': 'fa-file-code',
    '.sql': 'fa-file-code',

    # Default fallback
    'default': 'fa-file'
}

@register.filter
def file_icon(file_name):
    _, ext = os.path.splitext(file_name)
    return ICON_MAP.get(ext.lower(), 'fa-file')