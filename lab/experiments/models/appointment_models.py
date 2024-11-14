from datetime import datetime, timedelta

from cdh.mail.classes import TemplateEmail
from django.db import models
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from main.models import User
from participants.models import Participant

from .experiment_models import Experiment


class TimeSlot(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    start = models.DateTimeField(_("time_slot:attribute:start"))
    end = models.DateTimeField(_("time_slot:attribute:start"))

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(end__gt=models.F("start")), name="end_after_start"),
        ]

    @property
    def datetime(self):
        return self.start  # temporarily keep compatability

    def __str__(self):
        return "{}: {}".format(self.experiment.name, self.datetime)


class _Outcome(models.TextChoices):
    # appointment was succesfully completed
    COMPLETED = "COMPLETED", _("experiments:appointment:outcome:completed")
    # participant did not participate
    NOSHOW = "NOSHOW", _("experiments:appointment:outcome:noshow")
    # participant had to be excluded
    EXCLUDED = "EXCLUDED", _("experiments:appointment:outcome:excluded")
    # canceled appointment
    CANCELED = "CANCELED", _("experiments:appointment:outcome:canceled")


class Appointment(models.Model):
    # declaring _Outcome above is requried for refering to it in the UniqueConstraint
    Outcome = _Outcome

    participant = models.ForeignKey(Participant, on_delete=models.PROTECT, related_name="appointments")
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name="appointments", null=True, blank=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name="appointments")
    leader = models.ForeignKey(User, on_delete=models.PROTECT, null=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=100, default="", blank=True)
    outcome = models.CharField(max_length=20, choices=Outcome.choices, null=True)
    updated = models.DateTimeField(auto_now=True)
    reminder_sent = models.DateTimeField(null=True)

    class Meta:
        ordering = ["creation_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["participant", "experiment"],
                condition=~models.Q(outcome__in=[_Outcome.CANCELED, _Outcome.EXCLUDED]),
                name="unique_appointment",
            ),
        ]

    def save(self, *args, **kwargs):
        # verify that the leader is valid
        if self.leader not in self.experiment.leaders.all():
            raise ValueError("Leader {} is not part of experiment {}".format(self.leader, self.experiment))
        self.timeslot.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return "{} -> {}".format(self.participant, self.experiment.name)

    @property
    def start(self):
        return self.timeslot.start

    @start.setter
    def start(self, starttime):
        self.timeslot.start = starttime

    @property
    def end(self):
        return self.timeslot.end

    @end.setter
    def end(self, end_time):
        self.timeslot.end = end_time

    def location(self):
        # TODO: temporary workaround for missing locations
        return self.experiment.location.name if self.experiment.location else "Unknown"

    def cancel(self, silent=False):
        if self.outcome is None:
            self.outcome = Appointment.Outcome.CANCELED
            self.save()
            if not silent:
                _inform_leaders(self)
                _send_cancel_confirmation(self)

    @property
    def is_canceled(self):
        return self.outcome == Appointment.Outcome.CANCELED


def make_appointment(experiment: Experiment, participant: Participant, leader: User, start: datetime):
    if leader not in experiment.leaders.all():
        raise ValueError(f'{leader} is not a leader in the experiment "{experiment}"')

    # appointment end is determined by the experiment's session duration
    end = start + timedelta(minutes=experiment.session_duration)
    timeslot = TimeSlot.objects.create(start=start, end=end, experiment=experiment)
    appointment = Appointment.objects.create(
        participant=participant, timeslot=timeslot, experiment=experiment, leader=leader
    )
    return appointment


def _inform_leaders(appointment: Appointment) -> None:
    experiment = appointment.experiment
    leaders = experiment.leaders.all()

    for leader in leaders:
        subject = "ILS appointment canceled by parent"
        context = {
            "appointment": appointment,
            "leader": leader,
        }

        mail = TemplateEmail(
            html_template="mail/appointment/canceled_leader.html",
            context=context,
            to=[leader.email],
            subject=subject,
        )
        mail.send()


def _send_cancel_confirmation(appointment: Appointment) -> None:
    context = {"appointment": appointment}

    with translation.override("nl"):
        mail = TemplateEmail(
            html_template="mail/appointment/canceled.html",
            context=context,
            to=[appointment.participant.email],
            subject=_("experiments:mail:appointment:canceled:subject"),
        )
        mail.send()
