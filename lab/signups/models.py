import cdh.core.fields as e_fields
from django.db import models
from django.utils.translation import gettext_lazy as _


class Signup(models.Model):
    name = e_fields.EncryptedCharField(max_length=100)
    sex = e_fields.EncryptedCharField(max_length=1)
    birth_date = e_fields.EncryptedDateField()

    parent_name = e_fields.EncryptedTextField()
    city = e_fields.EncryptedTextField()
    phonenumber = e_fields.EncryptedTextField()
    phonenumber_alt = e_fields.EncryptedTextField(blank=True)
    email = e_fields.EncryptedTextField()

    english_contact = e_fields.EncryptedBooleanField()
    newsletter = e_fields.EncryptedBooleanField()

    dyslexic_parent = e_fields.EncryptedBooleanField()
    tos_parent = e_fields.EncryptedBooleanField()
    speech_parent = e_fields.EncryptedBooleanField()
    multilingual = e_fields.EncryptedBooleanField()

    class Status(models.TextChoices):
        NEW = 'NEW', _('signups:stats:new')
        APPROVED = 'APPROVED', _('signups:stats:approved')
        REJECTED = 'REJECTED', _('signups:stats:rejected')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    created = models.DateTimeField(auto_now_add=True)
