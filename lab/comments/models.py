from django.db import models
from django.utils.translation import gettext_lazy as _

import cdh.core.fields as e_fields
from participants.models import Participant
from main.models import User


class Comment(models.Model):

    class Meta:
        ordering = ('-id',)

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        verbose_name=_('comment:attribute:participant'),
    )

    leader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('comment:attribute:leader'),
        null=True,
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

    system_comment = models.BooleanField(
        verbose_name=_('comment:attribute:datetime'),
        default=False
    )

    def __str__(self):
        return "{}: {} ({})".format(
            self.leader or "admin",
            self.comment,
            self.participant.name,
        )
