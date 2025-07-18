from datetime import datetime, timedelta

import cdh.files.db
from django.db import models
from django.urls import reverse
from django.utils.timezone import get_current_timezone
from django.utils.translation import gettext_lazy as _

from main.models import User

from ..email import (
    DEFAULT_CONFIRMATION_MAIL,
    DEFAULT_REMINDER_MAIL,
    AppointmentConfirmEmail,
    AppointmentReminderEmail,
)
from .default_criteria_models import DefaultCriteria
from .location_models import Location


def _get_dt_2_hours_ago() -> datetime:
    return datetime.now(tz=get_current_timezone()) - timedelta(hours=2)


class Experiment(models.Model):
    name = models.TextField(_("experiment:attribute:name"))

    duration = models.IntegerField(
        _("experiment:attribute:duration"), help_text=_("experiment:attribute:duration:help_text")
    )

    session_duration = models.IntegerField(
        _("experiment:attribute:session_duration"), help_text=_("experiment:attribute:session_duration:help_text")
    )

    # how many participants are aimed for
    recruitment_target = models.PositiveIntegerField(
        _("experiment:attribute:recruitment_target"),
        default=0,
    )

    task_description = models.TextField(_("experiment:attribute:task_description"))

    confirmation_email = models.TextField(
        _("experiment:attribute:confirmation_email"),
        help_text=AppointmentConfirmEmail.help_text,
        default=DEFAULT_CONFIRMATION_MAIL,
    )

    reminder_email = models.TextField(
        _("experiment:attribute:reminder_email"),
        help_text=AppointmentReminderEmail.help_text,
        default=DEFAULT_REMINDER_MAIL,
    )

    send_reminders = models.BooleanField(
        _("experiment:attribute:send_reminders"),
        help_text=_("experiment:attribute:send_reminders:help_text"),
        default=True,
    )

    location = models.ForeignKey(
        Location,
        verbose_name=_("experiment:attribute:location"),
        on_delete=models.SET_NULL,
        null=True,
    )

    excluded_experiments = models.ManyToManyField(
        "self",
        verbose_name=_("experiment:attribute:excluded_experiments"),
        blank=True,
        help_text=_("experiment:attribute:excluded_experiments:help_text"),
        symmetrical=False,
        related_name="experiments_excluding",
    )

    required_experiments = models.ManyToManyField(
        "self",
        verbose_name=_("experiment:attribute:required_experiments"),
        blank=True,
        help_text=_("experiment:attribute:required_experiments:help_text"),
        symmetrical=False,
        related_name="experiments_requiring",
    )

    leaders = models.ManyToManyField(
        User,
        verbose_name=_("experiment:attribute:leaders"),
        related_name="experiments",
        blank=False,
        help_text=_("experiment:attribute:leaders:help_text"),
    )

    responsible_researcher = models.TextField(
        _("experiment:attribute:responsible_researcher"),
        help_text=_("experiment:attribute:responsible_researcher:help_text"),
    )

    defaultcriteria = models.OneToOneField(DefaultCriteria, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """Run models.save but make sure the experiment has default criteria"""
        try:
            no_createria = self.defaultcriteria is None
            if no_createria:
                self.defaultcriteria = DefaultCriteria.objects.create()
        except Experiment.defaultcriteria.RelatedObjectDoesNotExist:
            self.defaultcriteria = DefaultCriteria.objects.create()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def leader_names(self):
        # TODO: i18n? (for connective 'en' -> 'and')
        leader_names = [leader.name for leader in self.leaders.all()]
        return "".join(f"{name}, " for name in leader_names[:-2]) + " en ".join(leader_names[-2:])

    def is_leader(self, user: User) -> bool:
        return user.experiments.filter(pk=self.pk).exists()


class ConfirmationMailAttachment(models.Model):
    filename = models.CharField(max_length=255)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="attachments")
    created = models.DateTimeField(auto_now_add=True)
    file = cdh.files.db.FileField()

    @property
    def link(self):
        return reverse(
            "experiments:attachment",
            args=(
                self.experiment.pk,
                self.pk,
            ),
        )
