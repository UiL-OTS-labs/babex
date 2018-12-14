from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .experiment_models import Experiment


class DefaultCriteria(models.Model):
    MULTILINGUAL = (
        ('Y', _('default_criteria:attribute:multilingual:yes')),
        ('N', _('default_criteria:attribute:multilingual:no')),
        ('I', _('experiments:globals:indifferent')),
    )

    SEX = (
        ('M', _('default_criteria:attribute:sex:male')),
        ('F', _('default_criteria:attribute:sex:female')),
        ('I', _('experiments:globals:indifferent')),
    )

    HANDEDNESS = (
        ('L', _('default_criteria:attribute:handedness:lefthanded')),
        ('R', _('default_criteria:attribute:handedness:righthanded')),
        ('I', _('experiments:globals:indifferent')),
    )

    DYSLEXIA = (
        ('Y', _('default_criteria:attribute:dyslexia:yes')),
        ('N', _('default_criteria:attribute:dyslexia:no')),
        # ('I', _('experiments:globals:indifferent')),
    )

    SOCIAL_STATUS = (
        ('S', _('default_criteria:attribute:social_status:student')),
        ('O', _('default_criteria:attribute:social_status:other')),
        ('I', _('experiments:globals:indifferent')),
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
        default='I',
    )

    sex = models.CharField(
        _('default_criteria:attribute:sex'),
        choices=SEX,
        max_length=1,
        blank=False,
        default='I',
    )

    handedness = models.CharField(
        _('default_criteria:attribute:handedness'),
        choices=HANDEDNESS,
        max_length=1,
        blank=False,
        default='I',
    )

    dyslexia = models.CharField(
        _('default_criteria:attribute:dyslexia'),
        choices=DYSLEXIA,
        max_length=1,
        blank=False,
        default='I',
    )

    social_status = models.CharField(
        _('default_criteria:attribute:social_status'),
        choices=SOCIAL_STATUS,
        max_length=1,
        blank=False,
        default='I',
    )

    min_age = models.IntegerField(
        _('default_criteria:attribute:min_age'),
        validators=[MinValueValidator(-1)],
        default=-1,
        help_text=_('default_criteria:attribute:min_age:help_text'),
    )

    max_age = models.IntegerField(
        _('default_criteria:attribute:max_age'),
        validators=[MinValueValidator(-1)],
        default=-1,
        help_text=_('default_criteria:attribute:max_age:help_text'),
    )

    def get_min_age_display(self):
        if self.min_age == -1:
            return _('experiments:globals:indifferent')

        return self.min_age

    def get_max_age_display(self):
        if self.max_age == -1:
            return _('experiments:globals:indifferent')

        return self.max_age


class Criterium(models.Model):
    class Meta:
        ordering = ('name_natural',)

    name_form = models.TextField(
        _('criterium:attribute:name_form'),
    )

    name_natural = models.TextField(
        _('criterium:attribute:name_natural'),
    )

    values = models.TextField(
        _('criterium:attribute:values'),
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


class ExperimentCriterium(models.Model):

    criterium = models.ForeignKey(
        Criterium,
        on_delete=models.CASCADE,
    )

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
    )

    correct_value = models.TextField(
        _('experiment_criterium:attribute:correct_value'),
    )

    message_failed = models.TextField(
        _('experiment_criterium:attribute:message_failed'),
    )
