from django.db import models
from django.utils.translation import gettext_lazy as _

from .experiment_models import Experiment


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
