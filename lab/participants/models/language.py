import cdh.core.fields as e_fields
from django.db import models

from utils.models import EncryptedManager


class Language(models.Model):
    objects = EncryptedManager()

    name = e_fields.EncryptedCharField(max_length=100)

    def __str__(self):
        return self.name
