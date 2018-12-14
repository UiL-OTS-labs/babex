from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _

from participants.models import Participant
from .experiment_models import Experiment
from ..utils import enumerate_to


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

    @property
    def places(self) -> list:
        """Returns a list of places with a corresponding participant (if any)"""
        return [{
            'n':           n,
            'appointment': appointment
        } for n, appointment in enumerate_to(self.appointments.all(),
                                             self.max_places, 1)]

    def has_free_places(self) -> bool:
        return self.appointments.count() < self.max_places

    @property
    def free_places(self) -> int:
        return self.max_places - self.appointments.count()


class Appointment(models.Model):

    class Meta:
        ordering = ['creation_date']

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='appointments',
    )

    timeslot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='appointments',
    )

    creation_date = models.DateTimeField(
        auto_now_add=True,
    )