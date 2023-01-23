from django.db import models
from django.utils.translation import gettext_lazy as _

from participants.models import Participant
from .experiment_models import Experiment
from main.models import User


class Invitation(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Invitation for {} for {}".format(
            self.experiment.name,
            self.participant.name,
        )


class Call(models.Model):
    class CallStatus(models.TextChoices):
        # call status copied as-is from old babylab system
        STARTED = 'STARTED', _('experiments:call:status:started')
        NOREPLY = 'NOREPLY', _('experiments:call:status:noreply')
        CALLBACK = 'CALLBACK', _('experiments:call:status:callback')
        VOICEMAIL = 'VOICEMAIL', _('experiments:call:status:voicemail')
        EMAIL = 'EMAIL', _('experiments:call:status:email')
        CONFIRMED = 'CONFIRMED', _('experiments:call:status:confirmed')
        CANCELLED = 'CANCELLED', _('experiments:call:status:cancelled')

    status = models.CharField(max_length=20, choices=CallStatus.choices, default=CallStatus.STARTED)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    leader = models.ForeignKey(User,
                               # don't delete old calls just because the caller is gone
                               on_delete=models.PROTECT)

    creation_date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True)
