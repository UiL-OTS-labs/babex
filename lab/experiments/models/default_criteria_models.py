from functools import partialmethod

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from participants.models.enums import BirthWeight, PregnancyDuration, Sex


class CriterionField(models.JSONField):
    def __init__(self, *args, **kwargs):
        # choices should always be defined, but sometimes they are not
        # when this is called from within django's migration code
        if "choices" in kwargs:
            # the following line prevents the underlying django code from seeing the specified choices,
            # but these are saved in 'self.options'.
            # this is done because we need to know the possible options, but we don't want django's default behaviour
            # to limit the values that can be saved to the database, because any combination of choices is valid.
            # (see also DefaultCriteriaForm)
            self.options = kwargs.pop("choices")
        kwargs["null"] = True
        kwargs["blank"] = False
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, private_only=False):
        # this is based on Django's built-in code to generate a get_{field}_display method
        def display_func(model, field):
            values = set(getattr(model, field.attname) or [])
            return ", ".join([str(choice[1]) for choice in self.options if choice[0] in values])

        setattr(cls, "get_%s_display" % name, partialmethod(display_func, field=self))

        super().contribute_to_class(cls, name, private_only)


class DefaultCriteria(models.Model):
    YESNO = (
        ("Y", _("default_criteria:attribute:yes")),
        ("N", _("default_criteria:attribute:no")),
    )

    multilingual = CriterionField(_("default_criteria:attribute:multilingual"), choices=YESNO)
    sex = CriterionField(_("default_criteria:attribute:sex"), choices=Sex.choices)
    dyslexic_parent = CriterionField(_("default_criteria:attribute:dyslexic_parent"), choices=YESNO)
    birth_weight = CriterionField(
        _("default_criteria:attribute:birth_weight"),
        choices=BirthWeight.choices,
    )
    pregnancy_duration = CriterionField(
        _("default_criteria:attribute:pregnancy_duration"),
        choices=PregnancyDuration.choices,
    )
    tos_parent = CriterionField(_("default_criteria:attribute:tos_parent"), choices=YESNO)

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
