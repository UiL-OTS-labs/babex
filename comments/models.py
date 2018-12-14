from django.db import models
from django.utils.translation import ugettext_lazy as _

import main.fields as e_fields
from experiments.models import Experiment
from leaders.models import Leader
from participants.models import Participant


class Comment(models.Model):

    class Meta:
        ordering = ('-id',)

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        verbose_name=_('comment:attribute:participant'),
    )

    leader = models.ForeignKey(
        Leader,
        on_delete=models.CASCADE,
        verbose_name=_('comment:attribute:leader'),
        null=True,
    )

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        verbose_name=_('comment:attribute:experiment'),
    )

    comment = e_fields.EncryptedTextField(
        verbose_name=_('comment:attribute:comment'),
    )

    datetime = models.DateTimeField(
        verbose_name=_('comment:attribute:datetime'),
        blank=True,
        null=True,
        auto_now_add=True,
    )
