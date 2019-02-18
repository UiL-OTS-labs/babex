from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register([
    Experiment,
    ExperimentCriterion,
    Criterion,
    DefaultCriteria,
    TimeSlot,
    Appointment,
    Location
])
