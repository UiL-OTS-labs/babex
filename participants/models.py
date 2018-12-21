from datetime import date

from django.db import models
from django.utils.translation import ugettext_lazy as _

import main.fields as e_fields
from api.auth.models import ApiUser
from experiments.models.criteria_models import Criterium


class Participant(models.Model):

    HANDEDNESS = (
        ('L', _('participant:attribute:handedness:lefthanded')),
        ('R', _('participant:attribute:handedness:righthanded')),
    )

    # Yes, this is controversial. I'm sorry!
    SEX = (
        ('M', _('participant:attribute:sex:male')),
        ('F', _('participant:attribute:sex:female')),
    )

    SOCIAL_STATUS = (
        ('S', _('participant:attribute:social_role:student')),
        ('O', _('participant:attribute:social_role:other')),
    )

    email = e_fields.EncryptedEmailField(
        _('participant:attribute:email'),
    )

    name = e_fields.EncryptedTextField(
        _('participant:attribute:name'),
        blank=True,
        null=True,
    )

    language = e_fields.EncryptedTextField(
        _('participant:attribute:language'),
    )

    dyslexic = e_fields.EncryptedBooleanField(
        _('participant:attribute:dyslexic'),
    )

    birth_date = e_fields.EncryptedDateField(
        _('participant:attribute:birth_date'),
        blank=True,
        null=True,
    )

    # NOTE: When updating to Django 2.1 you should change this to a regular
    # BooleanField
    multilingual = e_fields.EncryptedNullBooleanField(
        _('participant:attribute:multilingual'),
        blank=True,
        null=True,
    )

    phonenumber = e_fields.EncryptedTextField(
        _('participant:attribute:phonenumber'),
        blank=True,
        null=True,
    )

    handedness = e_fields.EncryptedTextField(
        _('participant:attribute:handedness'),
        choices=HANDEDNESS,
        blank=True,
        null=True,
    )

    sex = e_fields.EncryptedTextField(
        _('participant:attribute:sex'),
        choices=SEX,
        blank=True,
        null=True,
    )

    social_status = e_fields.EncryptedTextField(
        _('participant:attribute:social_status'),
        choices=SOCIAL_STATUS,
        blank=True,
        null=True,
    )

    email_subscription = e_fields.EncryptedBooleanField(
        _('participant:attribute:email_subscription'),
        default=False,
    )

    capable = e_fields.EncryptedBooleanField(
        _('participant:attribute:capable'),
        default=True,
    )

    api_user = models.OneToOneField(
        ApiUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    @property
    def fullname(self) -> str:
        if self.name:
            return self.name

        return _('participant:name:unknown')

    @property
    def mail_name(self) -> str:
        if self.name:
            return self.name

        return 'proefpersoon'

    @property
    def age(self) -> int:
        if self.birth_date:
            today = date.today()

            return today.year - self.birth_date.year - (
                        (today.month, today.day) < (self.birth_date.month, self.birth_date.day))

        return -1

    def __str__(self):
        name = self.fullname

        if not name:
            name = _('participant:name:unknown').__str__()

        return "[{}] {}".format(self.pk, name)


class SecondaryEmail(models.Model):
    email = e_fields.EncryptedEmailField(
        _('secondary_email:attribute:email'),
    )

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)

    def __str__(self):
        return self.email

    def __repr__(self):
        return "<SecondaryEmail ({})>".format(self.email)


class CriteriumAnswer(models.Model):

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)

    criterium = models.ForeignKey(Criterium, on_delete=models.CASCADE)

    answer = e_fields.EncryptedTextField(
        _('criterium_answer:attribute:answer')
    )
