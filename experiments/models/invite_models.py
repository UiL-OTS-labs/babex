from django.db import models

from participants.models import Participant
from .experiment_models import Experiment


class Invitation(models.Model):
    class Meta:
        unique_together = ('experiment', 'participant')

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
    )

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
    )
