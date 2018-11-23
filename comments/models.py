from django.db import models

from participants.models import Participant
from leaders.models import Leader
from experiments.models import Experiment


class Comment(models.Model):

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)

    leader = models.ForeignKey(Leader, on_delete=models.CASCADE)

    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    comment = models.TextField()
