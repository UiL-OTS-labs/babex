from datetime import date
from typing import List, Optional

from django.db import models
from django.utils.translation import gettext_lazy as _

import cdh.core.fields as e_fields
from api.auth.models import ApiUser
from experiments.models.criteria_models import Criterion


class ParticipantManager(models.Manager):

    def find_by_email(self, email: str) -> List['Participant']:
        """This function will return a list of Participants that have the
        given email address as a primary or secondary email.

        NOTE: this does NOT return a queryset, as the matching is done in
        python instead of the database!
        """

        def to_lower(string: str) -> str:
            return str(string).lower()

        email = email.strip().lower()

        # Get a QS with the secondary emails preloaded (to avoid n+1 database
        # calls)
        queryset = self.prefetch_related('secondaryemail_set')

        # This LC filters by checking if the email is the same, or appears in
        # the secondary email set.
        return [x for x in queryset if
                to_lower(x.email) == email
                or
                email in [
                    to_lower(y.email) for y in x.secondaryemail_set.all()]
                ]


class Participant(models.Model):
    objects = ParticipantManager()

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

    multilingual = e_fields.EncryptedBooleanField(
        _('participant:attribute:multilingual'),
        blank=True,
        null=True,
    )

    phonenumber = e_fields.EncryptedTextField(
        _('participant:attribute:phonenumber'),
        blank=True,
        null=True,
    )

    sex = e_fields.EncryptedTextField(
        _('participant:attribute:sex'),
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

    created = models.DateTimeField(
        verbose_name=_('participant:attribute:created'),
        auto_now_add=True,
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
    def age(self) -> Optional[int]:
        if self.birth_date:
            today = date.today()

            return today.year - self.birth_date.year - (
                    (today.month, today.day) < (
            self.birth_date.month, self.birth_date.day))

        return None

    def get_sex_display(self):
        mappings = {
            "M": _('participant:attribute:sex:male'),
            "F": _('participant:attribute:sex:female'),
            "PNTA": _('participant:attribute:sex:prefer_not_to_answer'),
            None: None
        }

        if self.sex in mappings:
            return mappings[self.sex]

        return self.sex

    @property
    def has_account(self):
        return self.api_user is not None

    def __str__(self):
        name = self.fullname

        if not name:
            name = _('participant:name:unknown').__str__()

        return "[{}] {} ({}, {})".format(
            self.pk,
            name,
            self.birth_date,
            self.phonenumber
        )


class SecondaryEmail(models.Model):
    email = e_fields.EncryptedEmailField(
        _('secondary_email:attribute:email'),
    )

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)

    def __str__(self):
        return self.email

    def __repr__(self):
        return "<SecondaryEmail ({})>".format(self.email)


class CriterionAnswer(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)

    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE)

    answer = e_fields.EncryptedTextField(
        _('criterion_answer:attribute:answer')
    )

    def __str__(self):
        return "({}) {}: {}".format(
            self.participant.name,
            self.criterion.name_natural,
            self.answer
        )
