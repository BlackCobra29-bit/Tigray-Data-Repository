from django import template
from django.utils.html import strip_tags
import os

register = template.Library()

@register.filter
def basename(value):
    
    return os.path.basename(value)

@register.filter
def read_more_content(value):
    
    return strip_tags(value).strip()[:100]