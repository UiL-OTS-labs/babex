from datetime import datetime, timedelta

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count, F
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import get_current_timezone

from leaders.models import Leader
from .default_criteria_models import DefaultCriteria
from .location_models import Location


def _get_dt_2_hours_ago() -> datetime:
    return datetime.now(tz=get_current_timezone()) - timedelta(hours=2)


class Experiment(models.Model):

    DEFAULT_CONFIRMATION_MAIL = """<p>Beste {participant_name},</p>
    <p>
        Je hebt een afspraak gemaakt om mee te doen met het experiment:
        <strong>{experiment_name}</strong><br/><br/>
        We verwachten je op:<br/><br/>
        Datum: <strong>{date}</strong><br/>
        Tijd: <strong>{time} uur</strong><br/>
        Locatie: <strong>{experiment_location}</strong><br/>
    </p>
    <p>
        Als je deze afspraak wilt afzeggen, kun je dat doen via
        {cancel_link:"deze link"}.
        Doe dat alsjeblieft minstens 24 uur vantevoren. Als je vlak vantevoren
        ontdekt dat je verhinderd bent, neem dan svp even persoonlijk contact
        op met de proefleider
        ({leader_name}, email: {leader_email} tel.: {leader_phonenumber}).
    </p>
    <p>
        Met vriendelijke groet,<br/>
        het UiL OTS lab
    </p>"""

    DEFAULT_INVITE_MAIL = """<p>Je kunt je weer opgeven voor een nieuw
    experiment: <strong>{experiment_name}</strong>.</p>
<p>De proefleider is <strong>{leader_name}</strong>.
<ul>
    <li>Duur: {duration}.</li>
    <li>Vergoeding: {compensation}.</li>
    <li>{task_description}</li>
    <li>{additional_instructions}</li>
</ul>

<p>Je kunt via {link_to_subscribe:"deze link"} inschrijven.</p>

<p>Bedankt!</p>

<p>
Met vriendelijke groet,<br/>
{admin}
</p>"""

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
        _('experiment:attribute:additional_instructions'),
        blank=True,
    )

    confirmation_email = models.TextField(
        _('experiment:attribute:confirmation_email'),
        help_text=_('experiment:attribute:confirmation_email:help_text'),
        default=DEFAULT_CONFIRMATION_MAIL,
    )

    invite_email = models.TextField(
        _('experiment:attribute:invite_email'),
        help_text=_('experiment:attribute:invite_email:help_text'),
        default=DEFAULT_INVITE_MAIL,
    )

    location = models.ForeignKey(
        Location,
        verbose_name=_('experiment:attribute:location'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    use_timeslots = models.BooleanField(
        _('experiment:attribute:use_timeslots'),
        default=True,
        help_text=_('experiment:attribute:use_timeslots:help_text'),
    )

    default_max_places = models.PositiveSmallIntegerField(
        _('experiment:attribute:default_max_places'),
        validators=[
            MinValueValidator(1),
        ],
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

    excluded_experiments = models.ManyToManyField(
        "self",
        verbose_name=_('experiment:attribute:excluded_experiments'),
        blank=True,
        help_text=_('experiment:attribute:excluded_experiments:help_text'),
    )

    leaders = models.ManyToManyField(
        Leader,
        verbose_name=_("experiment:attribute:leaders"),
        related_name='experiments',
        blank=True,
        help_text=_("experiment:attribute:leaders:help_text"),
    )

    defaultcriteria = models.OneToOneField(
        DefaultCriteria,
        on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        """Run models.save but make sure the experiment has default criteria"""
        try:
            no_createria = self.defaultcriteria is None
            if no_createria:
                self.defaultcriteria = DefaultCriteria.objects.create()
        except Experiment.defaultcriteria.RelatedObjectDoesNotExist:
            self.defaultcriteria = DefaultCriteria.objects.create()
        super().save(*args, **kwargs)

    def n_timeslot_places(self):
        """Returns the sum of all timeslot places this experiment has.
        Used for experiment index page. Used to be an aggregate method in
        that view, but it turns out it was not playing well with the other
        aggregates (it was taking those as a multiply number, due to weird
        join behaviour).

        This function is basically me giving up....
        """

        return sum([x.max_places for x in self.timeslot_set.all()])

    def has_free_places(self):
        """
        Returns if this experiment is available for new participants. If
        this experiment uses timeslots, it will return the same as
        has_free_timeslots. Otherwise, it will check if the number of existing
        appointments is lower than the number of maximum appointments.
        :return:
        """

        if self.use_timeslots:
            return self.has_free_timeslots()

        return self.appointments.count() < self.default_max_places

    def has_free_timeslots(self):
        """
        Returns if this experiment still has free timeslots available for
        registering. If this experiment does not use timeslots, it will always
        return False.
        :return:
        """

        return self.timeslot_set.annotate(
            num_appointments=Count('appointments')
        ).filter(
            datetime__gt=_get_dt_2_hours_ago(),
            max_places__gt=F('num_appointments')
        ).exists()

    def __str__(self):
        return self.name

    @property
    def leader_names(self):
        # TODO: i18n? (for connective 'en' -> 'and')
        leader_names = [leader.name for leader in self.leaders.all()]
        return ''.join(f'{name}, ' for name in leader_names[:-2]) + ' en '.join(leader_names[-2:])
