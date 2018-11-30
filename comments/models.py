from django.db import models
from django.utils.translation import ugettext_lazy as _

from participants.models import Participant
from leaders.models import Leader
from experiments.models import Experiment


class Comment(models.Model):

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        verbose_name=_('comment:attribute:participant'),
    )

    leader = models.ForeignKey(
        Leader,
        on_delete=models.CASCADE,
        verbose_name=_('comment:attribute:leader'),
    )

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        verbose_name=_('comment:attribute:experiment'),
    )

    comment = models.TextField(
        verbose_name=_('comment:attribute:comment'),
    )

    datetime = models.DateTimeField(
        verbose_name=_('comment:attribute:datetime'),
        blank=True,
        null=True,
    )
