from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class DefaultCriteria(models.Model):
    MULTILINGUAL = (
        ("N", _("default_criteria:attribute:multilingual:no")),
        ("Y", _("default_criteria:attribute:multilingual:yes")),
        ("I", _("experiments:globals:indifferent")),
    )

    SEX = (
        ("M", _("default_criteria:attribute:sex:male")),
        ("F", _("default_criteria:attribute:sex:female")),
        ("I", _("experiments:globals:indifferent")),
    )

    class Dyslexia(models.TextChoices):
        YES = "Y"
        NO = "N"
        INDIFFERENT = "I"

    DYSLEXIA = (
        (Dyslexia.YES, _("default_criteria:attribute:dyslexia:yes")),
        (Dyslexia.NO, _("default_criteria:attribute:dyslexia:no")),
        (Dyslexia.INDIFFERENT, _("experiments:globals:indifferent")),
    )

    multilingual = models.CharField(
        _("default_criteria:attribute:multilingual"),
        choices=MULTILINGUAL,
        max_length=1,
        blank=False,
        default="N",
    )

    sex = models.CharField(
        _("default_criteria:attribute:sex"),
        choices=SEX,
        max_length=1,
        blank=False,
        default="I",
    )

    dyslexia = models.CharField(
        _("default_criteria:attribute:dyslexia"),
        choices=DYSLEXIA,
        max_length=1,
        blank=False,
        default="N",
    )

    # age limits will be stored internally in two fields: months and days
    min_age_days = models.IntegerField(
        validators=[
            MinValueValidator(0),
            # 'months;days' age definitions are a bit wonky.
            # theoretically speaking, an experiment with a 0;30 to 1;0 age range is not well defined
            # (for example, a child born on February 1st will be 1 month old on March 1st, but less than 30 days old)
            # in practice, such undefined ranges should never happen, so we can safely limit days to max 28,
            # making sure the comparison between max and min ages is always well defined.
            MaxValueValidator(28),
        ],
        null=True,
        blank=True,
    )
    min_age_months = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    max_age_days = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(28),
        ],
        null=True,
        blank=True,
    )
    max_age_months = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)

    def get_min_age_display(self):
        if self.min_age_days is None and self.min_age_months is None:
            return _("experiments:globals:indifferent")

        return "{}; {}".format(self.min_age_months or 0, self.min_age_days or 0)

    def get_max_age_display(self):
        if self.max_age_days is None and self.max_age_months is None:
            return _("experiments:globals:indifferent")

        return "{}; {}".format(self.max_age_months or 0, self.max_age_days or 0)

    def __str__(self):
        return "Default criteria for {}".format(self.experiment.name)
