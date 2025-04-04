import datetime
from typing import List

import ageutil
from cdh.mail.classes import TemplateEmail
from django.db import models, transaction
from django.utils import timezone, translation
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from .participantdata import ParticipantData


class ParticipantManager(models.Manager):
    def create(self, **kwargs):
        data = ParticipantData.objects.create(**kwargs)
        return super().create(data=data)


class Participant(models.Model):
    from .enums import BirthWeight, PregnancyDuration, Sex, WhichParent

    objects = ParticipantManager()

    data = models.OneToOneField(ParticipantData, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(verbose_name=_("participant:attribute:created"), default=timezone.now)
    deactivated = models.DateTimeField(verbose_name=_("participant:attribute:deactivated"), null=True)

    @property
    def name(self):
        if self.data is None:
            return _("participants:deactivated:name")
        return self.data.name

    @property
    def sex(self):
        return self.data.sex

    @property
    def birth_date(self):
        return self.data.birth_date

    @property
    def birth_weight(self):
        return self.data.birth_weight

    @property
    def pregnancy_duration(self):
        return self.data.pregnancy_duration

    @property
    def languages(self):
        return self.data.languages

    @property
    def parent_first_name(self):
        return self.data.parent_first_name

    @property
    def parent_last_name(self):
        return self.data.parent_last_name

    @property
    def email(self):
        return self.data.email

    @property
    def phonenumber(self):
        return self.data.phonenumber

    @property
    def phonenumber_alt(self):
        return self.data.phonenumber_alt

    @property
    def dyslexic_parent(self):
        return self.data.dyslexic_parent

    @property
    def tos_parent(self):
        return self.data.tos_parent

    @property
    def save_longer(self):
        return self.data.save_longer

    @property
    def english_contact(self):
        return self.data.english_contact

    @property
    def email_subscription(self):
        return self.data.email_subscription

    @property
    def fullname(self):
        return self.name

    def get_sex_display(self):
        return self.data.get_sex_display()

    def get_birth_weight_display(self):
        return self.data.get_birth_weight_display()

    def get_pregnancy_duration_display(self):
        return self.data.get_pregnancy_duration_display()

    @property
    def dyslexic_parent_bool(self) -> bool | None:
        """this is used to translate the model field into a filter"""
        if self.dyslexic_parent in [
            self.WhichParent.FEMALE,
            self.WhichParent.MALE,
            self.WhichParent.BOTH,
        ]:
            return True
        elif self.dyslexic_parent == self.WhichParent.NEITHER:
            return False
        return None

    @property
    def tos_parent_bool(self) -> bool | None:
        """this is used to translate the model field into a filter"""
        if self.tos_parent in [
            self.WhichParent.FEMALE,
            self.WhichParent.MALE,
            self.WhichParent.BOTH,
        ]:
            return True
        elif self.tos_parent == self.WhichParent.NEITHER:
            return False
        return None

    def dyslexic_parent_display(self):
        return self.WhichParent(self.dyslexic_parent).label

    def tos_parent_display(self):
        return self.WhichParent(self.tos_parent).label

    @property
    def age(self):
        return ageutil.date_of_birth(self.birth_date).age_ymd()

    @property
    def age_short(self):
        return "{};{};{}".format(*self.age)

    @property
    def age_long(self):
        years, months, days = ageutil.date_of_birth(self.birth_date).age_ymd()
        return "{years} {years_str}; {months} {months_str}; {days} {days_str}".format(
            years_str=_("participants:age:years"),
            months_str=_("participants:age:months"),
            days_str=_("participants:age:days"),
            years=years,
            months=months,
            days=days,
        )

    @property
    def gestational_age(self):
        return self.PregnancyDuration[self.pregnancy_duration].label

    def deactivate(self, send_mail=False):
        # prepare mail before we remove all data
        with translation.override("nl"):
            mail = TemplateEmail(
                html_template="mail/removed.html",
                context=dict(parent_name=self.parent_name, participant_name=self.name),
                to=[self.email],
                subject=gettext("experiments:call:deactivate:mail:subject"),
            )

        with transaction.atomic():
            for appointment in self.appointments.all():
                appointment.cancel()
            self.data.delete()
            self.data = None
            self.extradata_set.all().delete()
            self.deactivated = timezone.now()
            self.save()

        if send_mail:
            mail.send()

    def can_be_deleted(self):
        # participants who have never participated may be removed without consequences
        return len(self.appointments.all()) < 1

    @property
    def parent_name(self):
        return f"{self.parent_first_name} {self.parent_last_name}"

    @property
    def multilingual(self):
        return self.languages.count() > 1

    @property
    def multilingual_bool(self):
        """basically an alias for self.multilingual, but required because of the exclusion filter assumptions"""
        return self.multilingual

    @property
    def languages_pretty(self):
        return ", ".join(self.languages.all().values_list("name", flat=True))

    @classmethod
    def find_by_email(cls, email: str) -> List["Participant"]:
        return [
            pd.participant
            for pd in ParticipantData.objects.efilter(email=email)
            if hasattr(pd, "participant") and pd.participant.deactivated is None
        ]

    @property
    def removal_date(self):
        threshold = ageutil.age(2, months=6)
        if self.save_longer:
            threshold = ageutil.age(10)

        return ageutil.date_of_birth(self.birth_date).range_for(threshold)[0]

    def is_removed_soon(self):
        return (self.removal_date - datetime.datetime.today().date()).days < 30
