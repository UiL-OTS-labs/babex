from django.db import models

from participants.models import Participant
from .experiment_models import Experiment


class Invitation(models.Model):

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
    )

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
    )

    creation_date = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return "Invitation for {} for {}".format(
            self.experiment.name,
            self.participant.name,
        )
