from django.db import models
from django.utils.translation import gettext_lazy as _


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
