import ageutil
import cdh.core.fields as e_fields
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from experiments.models.criteria_models import Criterion
from utils.models import EncryptedManager


class Language(models.Model):
    name = e_fields.EncryptedCharField(max_length=100)


class Participant(models.Model):
    class Sex(models.TextChoices):
        MALE = "M", _("participant:attribute:sex:male")
        FEMALE = "F", _("participant:attribute:sex:female")
        UNKNOWN = "UNK", _("participant:attribute:sex:prefer_not_to_answer")

    class WhichParent(models.TextChoices):
        MALE = "M", _("participant:attribute:which_parent:m")
        FEMALE = "F", _("participant:attribute:which_parent:f")
        BOTH = "BOTH", _("participant:attribute:which_parent:both")
        NEITHER = "NO", _("participant:attribute:which_parent:neither")
        UNKNOWN = "UNK", _("participant:attribute:which_parent:unk")

    class BirthWeight(models.TextChoices):
        LESS_THAN_2500 = "LESS_THAN_2500", _("participant:attribute:birth_weight:less_than_2500")
        _2500_TO_4500 = "2500_TO_4500", _("participant:attribute:birth_weight:2500_to_4500")
        MORE_THAN_4500 = "MORE_THAN_4500", _("participant:attribute:birth_weight:more_than_4500")

    class PregnancyDuration(models.TextChoices):
        LESS_THAN_37 = "LESS_THAN_37", _("participant:attribute:pregnancy_duration:less_than_37")
        _37_TO_42 = "37_TO_42", _("participant:attribute:pregnancy_duration:37_to_42")
        MORE_THAN_42 = "MORE_THAN_42", _("participant:attribute:pregnancy_duration:more_than_42")

    objects = EncryptedManager()

    name = e_fields.EncryptedTextField(_("participant:attribute:name"), blank=True, null=True)
    sex = e_fields.EncryptedTextField(_("participant:attribute:sex"), blank=True, null=True)
    birth_date = e_fields.EncryptedDateField(_("participant:attribute:birth_date"), blank=True, null=True)

    birth_weight = e_fields.EncryptedIntegerField(
        _("participant:attribute:birth_weight"), null=True, choices=BirthWeight.choices
    )
    pregnancy_duration = e_fields.EncryptedCharField(
        _("participant:attribute:pregnancy_duration"),
        null=True,
        choices=PregnancyDuration.choices,
        max_length=30,
    )
    languages = models.ManyToManyField(Language)

    parent_first_name = e_fields.EncryptedTextField(_("participant:attribute:parent_first_name"), null=True)
    parent_last_name = e_fields.EncryptedTextField(_("participant:attribute:parent_last_name"), null=True)
    email = e_fields.EncryptedEmailField(_("participant:attribute:email"))
    phonenumber = e_fields.EncryptedTextField(_("participant:attribute:phonenumber"), blank=True, null=True)
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

    created = models.DateTimeField(verbose_name=_("participant:attribute:created"), auto_now_add=True)
    deactivated = models.DateTimeField(verbose_name=_("participant:attribute:deactivated"), null=True)

    @property
    def fullname(self):
        return self.name

    def get_sex_display(self):
        return self.Sex(self.sex).label

    @property
    def dyslexic_parent_bool(self) -> bool | None:
        if self.dyslexic_parent in [
            self.WhichParent.FEMALE,
            self.WhichParent.MALE,
            self.WhichParent.BOTH,
        ]:
            return True
        elif self.dyslexic_parent == self.WhichParent.NEITHER:
            return False
        return None

    def dyslexic_parent_display(self):
        return self.WhichParent(self.dyslexic_parent).label

    def tos_parent_display(self):
        return self.WhichParent(self.tos_parent).label

    def __str__(self):
        name = self.fullname

        if not name:
            name = _("participant:name:unknown").__str__()

        return "[{}] {} ({}, {})".format(self.pk, name, self.birth_date, self.phonenumber)

    @property
    def age(self):
        return "{};{};{}".format(*ageutil.date_of_birth(self.birth_date).age_ymd())

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

    @property
    def last_call(self):
        return self.call_set.order_by("-creation_date").first()

    def deactivate(self):
        self.deactivated = timezone.now()
        self.save()

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
    def languages_pretty(self):
        return ", ".join(self.languages.all().values_list("name", flat=True))


# TODO: remove
class CriterionAnswer(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)

    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE)

    answer = e_fields.EncryptedTextField(_("criterion_answer:attribute:answer"))

    def __str__(self):
        return "({}) {}: {}".format(self.participant.name, self.criterion.name_natural, self.answer)
