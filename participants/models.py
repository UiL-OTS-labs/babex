from datetime import date
from typing import List, Optional

from django.db import models
from django.utils.translation import gettext_lazy as _

import ageutil
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

    email = e_fields.EncryptedEmailField(_('participant:attribute:email'),)
    name = e_fields.EncryptedTextField(_('participant:attribute:name'), blank=True, null=True,)
    language = e_fields.EncryptedTextField(_('participant:attribute:language'),)
    dyslexic_parent = e_fields.EncryptedBooleanField(_('participant:attribute:dyslexic_parent'),)
    birth_date = e_fields.EncryptedDateField(_('participant:attribute:birth_date'), blank=True, null=True,)
    multilingual = e_fields.EncryptedBooleanField(_('participant:attribute:multilingual'), blank=True, null=True,)
    phonenumber = e_fields.EncryptedTextField(_('participant:attribute:phonenumber'), blank=True, null=True,)
    sex = e_fields.EncryptedTextField(_('participant:attribute:sex'), blank=True, null=True,)
    email_subscription = e_fields.EncryptedBooleanField(_('participant:attribute:email_subscription'), default=False,)
    birth_weight = e_fields.EncryptedIntegerField(_('participant:attribute:birth_weight'), null=True)
    pregnancy_weeks = e_fields.EncryptedIntegerField(_('participant:attribute:pregnancy_weeks'), null=True)
    pregnancy_days = e_fields.EncryptedIntegerField(_('participant:attribute:pregnancy_days'), null=True)
    phonenumber_alt = e_fields.EncryptedTextField(_('participant:attribute:phonenumber_alt'), blank=True, null=True,)
    parent_name = e_fields.EncryptedTextField(_('participant:attribute:parent_name'), null=True)
    city = e_fields.EncryptedTextField(_('participant:attribute:city'), null=True)

    created = models.DateTimeField(verbose_name=_('participant:attribute:created'), auto_now_add=True,)

    # TODO: probably get rid of these
    api_user = models.OneToOneField(
        ApiUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    capable = e_fields.EncryptedBooleanField(_('participant:attribute:capable'), default=True,)


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

    @property
    def age(self):
        return '{};{};{}'.format(*ageutil.dob(self.birth_date).age_ymd())

    @property
    def age_long(self):
        years, months, days = ageutil.dob(self.birth_date).age_ymd()
        return '{years} {years_str}; {months} {months_str}; {days} {days_str}'.format(
            years_str=_('participants:age:years'),
            months_str=_('participants:age:months'),
            days_str=_('participants:age:days'),
            years=years, months=months, days=days)

    @property
    def gestational_age(self):
        if None not in [self.pregnancy_days, self.pregnancy_weeks]:
            return f'{self.pregnancy_weeks}; {self.pregnancy_days}'
        return ''

    @property
    def last_call(self):
        return self.call_set.order_by('-creation_date').first()


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
