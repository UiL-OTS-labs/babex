from django.contrib import admin

from .models import Experiment, DefaultCriteria, TimeSlot, Appointment, Location

# Register your models here.
admin.site.register([Experiment, DefaultCriteria, TimeSlot, Appointment, Location])
