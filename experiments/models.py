from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _


class Experiment(models.Model):

    name = models.TextField(
        _('experiment:attribute:name')
    )

    duration = models.TextField(
        _('experiment:attribute:duration')
    )

    compensation = models.TextField(
        _('experiment:attribute:compensation')
    )

    additional_instructions = models.TextField(
        _('experiment:attribute:additional_instructions')
    )

    location = models.TextField(
        _('experiment:attribute:location')
    )

    open = models.BooleanField(
        _('experiment:attribute:open')
    )

    public = models.BooleanField(
        _('experiment:attribute:public')
    )

    participants_visible = models.BooleanField(
        _('experiment:attribute:participants_visible')
    )

    excluded_experiments = models.ManyToManyField(
        "self",
        _('experiment:attribute:excluded_experiments')
    )


class TimeSlot(models.Model):

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE
    )

    datetime = models.DateTimeField(
        _('time_slot:attribute:datetime')
    )

    max_places = models.PositiveSmallIntegerField(
        _('time_slot:attribute:max_places'),
        validators=[MinValueValidator(1)]
    )