from django.db import models
from django.utils.translation import gettext_lazy as _


class Signup(models.Model):
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=1)
    birth_date = models.DateField()

    parent_name = models.TextField()
    city = models.TextField()
    phonenumber = models.TextField()
    phonenumber_alt = models.TextField(blank=True)
    email = models.TextField()

    english_contact = models.BooleanField()
    newsletter = models.BooleanField()

    dyslexic_parent = models.BooleanField()
    tos_parent = models.BooleanField()
    speech_parent = models.BooleanField()
    multilingual = models.BooleanField()

    class Status(models.TextChoices):
        NEW = 'NEW', _('signups:stats:new')
        APPROVED = 'APPROVED', _('signups:stats:approved')
        REJECTED = 'REJECTED', _('signups:stats:rejected')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
