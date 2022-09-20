from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .experiment_models import Experiment


class DefaultCriteria(models.Model):
    MULTILINGUAL = (
        ('N', _('default_criteria:attribute:multilingual:no')),
        ('Y', _('default_criteria:attribute:multilingual:yes')),
        ('I', _('experiments:globals:indifferent')),
    )

    SEX = (
        ('M', _('default_criteria:attribute:sex:male')),
        ('F', _('default_criteria:attribute:sex:female')),
        ('I', _('experiments:globals:indifferent')),
    )

    DYSLEXIA = (
        ('Y', _('default_criteria:attribute:dyslexia:yes')),
        ('N', _('default_criteria:attribute:dyslexia:no')),
        # ('I', _('experiments:globals:indifferent')),
    )

    experiment = models.OneToOneField(
        Experiment,
        on_delete=models.CASCADE
    )

    language = models.TextField(
        _('default_criteria:attribute:language'),
        default='nl',
    )

    multilingual = models.CharField(
        _('default_criteria:attribute:multilingual'),
        choices=MULTILINGUAL,
        max_length=1,
        blank=False,
        default='N',
    )

    sex = models.CharField(
        _('default_criteria:attribute:sex'),
        choices=SEX,
        max_length=1,
        blank=False,
        default='I',
    )

    dyslexia = models.CharField(
        _('default_criteria:attribute:dyslexia'),
        choices=DYSLEXIA,
        max_length=1,
        blank=False,
        default='N',
    )

    # age limits will be stored internally in two fields: months and days
    min_age_days = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    min_age_months = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    max_age_days = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    max_age_months = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)

    def get_language_display(self):
        if self.language == 'I':
            return _('experiments:globals:indifferent')

        return self.language

    def get_min_age_display(self):
        if self.min_age_days is None and self.min_age_months is None:
            return _('experiments:globals:indifferent')

        return '{}; {}'.format(self.min_age_months or 0, self.min_age_days or 0)

    def get_max_age_display(self):
        if self.max_age_days is None and self.max_age_months is None:
            return _('experiments:globals:indifferent')

        return '{}; {}'.format(self.max_age_months or 0, self.max_age_days or 0)

    def __str__(self):
        return "Default criteria for {}".format(self.experiment.name)


class Criterion(models.Model):
    class Meta:
        ordering = ('name_natural',)

    name_form = models.TextField(
        _('criterion:attribute:name_form'),
    )

    name_natural = models.TextField(
        _('criterion:attribute:name_natural'),
    )

    values = models.TextField(
        _('criterion:attribute:values'),
    )

    @property
    def values_list(self):
        return self.values.split(',')

    def formatted_values_str(self) -> str:
        return ", ".join(self.values_list)

    @property
    def choices_tuple(self) -> tuple:
        return tuple((x, x) for x in self.values_list)

    def __str__(self):
        return "{} ({})".format(
            self.name_natural,
            self.formatted_values_str()
        )


class ExperimentCriterion(models.Model):

    criterion = models.ForeignKey(
        Criterion,
        on_delete=models.CASCADE,
    )

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
    )

    correct_value = models.TextField(
        _('experiment_criterion:attribute:correct_value'),
    )

    message_failed = models.TextField(
        _('experiment_criterion:attribute:message_failed'),
    )

    def __str__(self):
        return "{} -> {}".format(
            self.criterion.name_natural,
            self.experiment.name,
        )
