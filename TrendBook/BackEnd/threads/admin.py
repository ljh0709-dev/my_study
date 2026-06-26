from django.contrib import admin

from .models import Comment, ReadingThread

admin.site.register(ReadingThread)
admin.site.register(Comment)
