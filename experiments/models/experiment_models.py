from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from .location_models import Location
from leaders.models import Leader


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

    @cached_property
    def _places_and_participants(self) -> dict:
        """Internal function, using a cache to minimize DB usage."""
        return self.timeslot_set.aggregate(
            places=models.Sum('max_places'),
            participants=models.Count('appointments'),
        )

    def get_number_of_places(self) -> int:
        """
        Returns the number of places in an experiment by counting the
        max_places for all timeslots.
        """
        return self._places_and_participants['places']

    def get_number_of_participants(self) -> int:
        """
        Returns the number of participants in an experiment by counting all
        participants in the timeslot set.
        """
        return self._places_and_participants['participants']

    def __str__(self):
        return self.name
