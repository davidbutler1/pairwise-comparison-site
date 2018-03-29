import os

from django import template
register = template.Library()

@register.filter
def index(List, i):
    return List[int(i)].file.url

@register.filter
def is_video(i):
    name, extension = os.path.splitext(i)
    if extension == '.mp4':
        return True
    if extension == '.webm':
        return True
    if extension == '.3gp':
        return True
    if extension == '.mpeg':
        return True
    if extension == '.mkv':
        return True

    return False
