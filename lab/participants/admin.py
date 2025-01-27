from django.contrib import admin

from .models import Language, Participant

# Register your models here.
admin.site.register([Participant, Language])
