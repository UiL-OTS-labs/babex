from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _


from .location_models import Location
from leaders.models import Leader
from participants.models import Participant


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
        validators=[MinValueValidator(1)],
        help_text=_('experiment:attribute:default_max_places:help_text'),
        default=1,
    )

    open = models.BooleanField(
        _('experiment:attribute:open'),
        default=False,
        help_text=_('experiment:attribute:open:help_text'),
    )

    public = models.BooleanField(
        _('experiment:attribute:public'),
        default=True,
        help_text=_('experiment:attribute:public:help_text'),
    )

    participants_visible = models.BooleanField(
        _('experiment:attribute:participants_visible'),
        default=True,
        help_text=_('experiment:attribute:participants_visible:help_text'),
    )

    excluded_experiments = models.ManyToManyField(
        "self",
        verbose_name=_('experiment:attribute:excluded_experiments'),
        blank=True,
        help_text=_('experiment:attribute:excluded_experiments:help_text'),
    )

    leader = models.ForeignKey(
        Leader,
        verbose_name=_("experiment:attribute:leader"),
        on_delete=models.SET_DEFAULT,
        related_name='experiments',
        default=1,
        help_text=_("experiment:attribute:leader:help_text"),
    )

    additional_leaders = models.ManyToManyField(
        Leader,
        verbose_name=_("experiment:attribute:additional_leaders"),
        related_name='secondary_experiments',
        blank=True,
        help_text=_("experiment:attribute:additional_leaders:help_text"),
    )

    def __str__(self):
        return self.name


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

    participants = models.ManyToManyField(
        Participant,
        verbose_name=_('time_slot:attribute:participants')
    )

    def has_free_places(self) -> bool:
        return self.participants.count() < self.max_places

    @property
    def free_places(self) -> int:
        return self.max_places - self.participants.count()
