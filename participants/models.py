from django.db import models
from django.utils.translation import ugettext_lazy as _

from api.auth.models import ApiUser
from experiments.models.criteria_models import Criterium


# TODO: encrypted fields!
# TODO: criteria saving!

class Participant(models.Model):

    HANDEDNESS = (
        ('left', _('participant:attribute:handedness:lefthanded')),
        ('right', _('participant:attribute:handedness:righthanded')),
    )

    # Yes, this is controversial. I'm sorry!
    SEX = (
        ('M', _('participant:attribute:sex:male')),
        ('F', _('participant:attribute:sex:female')),
    )

    SOCIAL_STATUS = (
        ('student', _('participant:attribute:social_role:student')),
        ('other', _('participant:attribute:social_role:other')),
    )

    email = models.EmailField(
        _('participant:attribute:email'),
    )

    name = models.TextField(
        _('participant:attribute:name'),
        blank=True,
        null=True,
    )

    language = models.TextField(
        _('participant:attribute:language'),
    )

    dyslexic = models.BooleanField(
        _('participant:attribute:dyslexic'),
    )

    birth_date = models.DateField(
        _('participant:attribute:birth_date'),
        blank=True,
        null=True,
    )

    # NOTE: When updating to Django 2.1 you should change this to a regular
    # BooleanField
    multilingual = models.NullBooleanField(
        _('participant:attribute:multilingual'),
        blank=True,
        null=True,
    )

    phonenumber = models.TextField(
        _('participant:attribute:phonenumber'),
        blank=True,
        null=True,
    )

    handedness = models.TextField(
        _('participant:attribute:handedness'),
        choices=HANDEDNESS,
        blank=True,
        null=True,
    )

    sex = models.TextField(
        _('participant:attribute:sex'),
        choices=SEX,
        blank=True,
        null=True,
    )

    social_status = models.TextField(
        _('participant:attribute:social_status'),
        choices=SOCIAL_STATUS,
        blank=True,
        null=True,
    )

    email_subscription = models.BooleanField(
        _('participant:attribute:email_subscription'),
        default=False,
    )

    capable = models.BooleanField(
        _('participant:attribute:capable'),
        default=True,
    )

    api_user = models.OneToOneField(
        ApiUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )


class SecondaryEmail(models.Model):
    email = models.EmailField(
        _('secondary_email:attribute:email'),
    )

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)


# class CriteriaAnswer(models.Model):
#
#     participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
#
#     criteria = models.ForeignKey(Criterium, on_delete=models.CASCADE)
#
#     answer = models.TextField()
