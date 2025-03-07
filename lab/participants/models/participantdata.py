import cdh.core.fields as e_fields
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.models import EncryptedManager

from .enums import BirthWeight, PregnancyDuration, Sex, WhichParent
from .language import Language


class ParticipantData(models.Model):
    objects = EncryptedManager()

    name = e_fields.EncryptedTextField(_("participant:attribute:name"), blank=True)
    sex = e_fields.EncryptedTextField(_("participant:attribute:sex"), choices=Sex.choices)
    birth_date = e_fields.EncryptedDateField(_("participant:attribute:birth_date"), blank=True)

    birth_weight = e_fields.EncryptedCharField(
        _("participant:attribute:birth_weight"), choices=BirthWeight.choices, max_length=30
    )
    pregnancy_duration = e_fields.EncryptedCharField(
        _("participant:attribute:pregnancy_duration"),
        choices=PregnancyDuration.choices,
        max_length=30,
    )
    languages = models.ManyToManyField(Language, verbose_name=_("participant:attribute:languages"))

    parent_first_name = e_fields.EncryptedTextField(_("participant:attribute:parent_first_name"))
    parent_last_name = e_fields.EncryptedTextField(_("participant:attribute:parent_last_name"))
    email = e_fields.EncryptedEmailField(_("participant:attribute:email"))
    phonenumber = e_fields.EncryptedTextField(_("participant:attribute:phonenumber"), blank=True)
    phonenumber_alt = e_fields.EncryptedTextField(_("participant:attribute:phonenumber_alt"), blank=True, null=True)

    dyslexic_parent = e_fields.EncryptedCharField(
        _("participant:attribute:dyslexic_parent"), max_length=5, choices=WhichParent.choices
    )
    tos_parent = e_fields.EncryptedCharField(
        _("participant:attribute:dyslexic_parent"), max_length=5, choices=WhichParent.choices
    )

    save_longer = e_fields.EncryptedBooleanField(_("participant:attribute:save_longer"), default=False)
    english_contact = e_fields.EncryptedBooleanField(_("participant:attribute:english_contact"), default=False)
    email_subscription = e_fields.EncryptedBooleanField(_("participant:attribute:email_subscription"), default=False)
