from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Count, F, Func, fields
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from leaders.models import Leader
from .location_models import Location


class TwoHoursAgo(Func):
    template = 'NOW() - INTERVAL 2 HOUR'
    output_field = fields.DateTimeField()

    def as_sqlite(self, compiler, connection, **extra_context):
        return self.as_sql(
            compiler,
            connection,
            template='date(\'now\', \'-2 hours\')'
        )


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
            datetime__gt=TwoHoursAgo(),
            max_places__gt=F('num_appointments')
        ).exists()

    def __str__(self):
        return self.name
