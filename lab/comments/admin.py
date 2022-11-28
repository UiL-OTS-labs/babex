from django.contrib import admin

# Register your models here.
from comments.models import Comment

admin.site.register(Comment)