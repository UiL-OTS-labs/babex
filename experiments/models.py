from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _

from leaders.models import Leader


class Location(models.Model):

    name = models.TextField(
        _('location:attribute:name'),
    )

    route_url = models.URLField(
        _('location:attribute:route_url'),
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class Experiment(models.Model):

    name = models.TextField(
        _('experiment:attribute:name')
    )

    duration = models.TextField(
        _('experiment:attribute:duration')
    )

    compensation = models.TextField(
        _('experiment:attribute:compensation')
    )

    task_description = models.TextField(
        _('experiment:attribute:task_description')
    )

    additional_instructions = models.TextField(
        _('experiment:attribute:additional_instructions')
    )

    location = models.ForeignKey(
        Location,
        verbose_name=_('experiment:attribute:location'),
        on_delete=models.SET_DEFAULT,
        default=1
    )

    default_max_places = models.PositiveSmallIntegerField(
        _('experiment:attribute:default_max_places'),
        validators=[MinValueValidator(1)]
    )

    open = models.BooleanField(
        _('experiment:attribute:open')
    )

    public = models.BooleanField(
        _('experiment:attribute:public')
    )

    participants_visible = models.BooleanField(
        _('experiment:attribute:participants_visible')
    )

    excluded_experiments = models.ManyToManyField(
        "self",
        verbose_name=_('experiment:attribute:excluded_experiments'),
        blank=True
    )

    leader = models.ForeignKey(
        Leader,
        verbose_name=_("experiment:attribute:leader"),
        on_delete=models.SET_DEFAULT,
        related_name='experiments',
        default=1
    )

    additional_leaders = models.ManyToManyField(
        Leader,
        verbose_name=_("experiment:attribute:additional_leaders"),
        related_name='secondary_experiments',
        blank=True
    )

    def __str__(self):
        return self.name


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
        ('I', _('experiments:globals:indifferent')),
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
        default='nl'
    )

    multilingual = models.CharField(
        _('default_criteria:attribute:multilingual'),
        choices=MULTILINGUAL,
        max_length=1,
    )

    sex = models.CharField(
        _('default_criteria:attribute:sex'),
        choices=SEX,
        max_length=1,
    )

    handedness = models.CharField(
        _('default_criteria:attribute:handedness'),
        choices=HANDEDNESS,
        max_length=1,
    )

    dyslexia = models.CharField(
        _('default_criteria:attribute:dyslexia'),
        choices=DYSLEXIA,
        max_length=1
    )

    social_status = models.CharField(
        _('default_criteria:attribute:social_status'),
        choices=SOCIAL_STATUS,
        max_length=1
    )

    min_age = models.IntegerField(
        _('default_criteria:attribute:min_age'),
        validators=[MinValueValidator(-1)],
    )

    max_age = models.IntegerField(
        _('default_criteria:attribute:max_age'),
        validators=[MinValueValidator(-1)],
    )


class TimeSlot(models.Model):

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE
    )

    datetime = models.DateTimeField(
        _('time_slot:attribute:datetime')
    )

    max_places = models.PositiveSmallIntegerField(
        _('time_slot:attribute:max_places'),
        validators=[MinValueValidator(1)]
    )
