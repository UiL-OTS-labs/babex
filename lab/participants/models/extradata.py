import cdh.core.fields as e_fields
from django.db import models
from django.utils.translation import gettext_lazy as _

from .participant import Participant


class ExtraData(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    title = e_fields.EncryptedCharField(max_length=255, verbose_name=_("extradata:attribute:title"))
    created = e_fields.EncryptedDateTimeField(verbose_name=_("extradata:attribute:created"), auto_now_add=True)
    content = e_fields.EncryptedTextField()
