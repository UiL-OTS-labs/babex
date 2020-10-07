from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from participants.models import Participant
from .experiment_models import Experiment
from uil.core.utils import enumerate_to


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
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ]
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

    def __str__(self):
        return "{}: {}".format(
            self.experiment.name,
            self.datetime
        )


class Appointment(models.Model):

    class Meta:
        ordering = ['creation_date']

    participant = models.ForeignKey(
        Participant,
        on_delete=models.PROTECT,
        related_name='appointments',
    )

    timeslot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='appointments',
        null=True,
        blank=True,
    )

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='appointments',
    )

    creation_date = models.DateTimeField(
        auto_now_add=True,
    )

    @cached_property
    def place(self):
        places = self.timeslot.places

        for place in places:
            if place['appointment'].pk == self.pk:
                return place['n']

        return -1

    def __str__(self):
        return "{} -> {}".format(
            self.participant,
            self.experiment.name
        )
