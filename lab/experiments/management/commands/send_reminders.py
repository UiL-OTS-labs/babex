import logging
from datetime import datetime, timedelta

from cdh.mail.classes import BaseEmail, _strip_tags
from django.core.mail import get_connection
from django.core.management.base import BaseCommand
from django.template import defaultfilters
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _

from experiments.email import AppointmentReminderEmail
from experiments.models import Appointment

logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger("send_reminders")


def prepare_reminder_mail(appointment: Appointment):
    experiment = appointment.experiment
    participant = appointment.participant
    time_slot = appointment.timeslot

    # override locale to force dates to use Dutch weekdays
    with translation.override("nl"):
        replacements = {
            "experiment_name": experiment.name,
            "experiment_location": "",
            "experiment_duration": experiment.duration,
            "session_duration": experiment.session_duration,
            "participant_name": participant.name,
            "parent_name": participant.parent_name,
            "leader_name": appointment.leader.name,
            "leader_email": appointment.leader.email,
            "leader_phonenumber": appointment.leader.phonenumber,
            "all_leaders_name_list": experiment.leader_names,
            "date": defaultfilters.date(timezone.localtime(time_slot.start), "l d-m-Y"),
            "time": defaultfilters.date(timezone.localtime(time_slot.start), "H:i"),
        }

    subject = _("experiments:mail:appointment:reminder:subject").format(appointment.experiment.name)

    if experiment.location:
        replacements["experiment_location"] = experiment.location.name

    email = AppointmentReminderEmail(
        [participant.email],
        subject,
        contents=experiment.confirmation_email,
    )
    email.context = replacements
    return email._get_html_body()


def send_reminder_mail(appointment: Appointment, contents: str) -> None:
    with translation.override("nl"):
        subject = _("experiments:mail:appointment:reminder:subject").format(appointment.experiment.name)

    class SimpleHTMLMail(BaseEmail):
        def __init__(self, to, subject, contents, **kwargs):
            super().__init__(to, subject, **kwargs)
            self.contents = contents

        def _get_html_context(self):
            return dict()

        def _get_html_body(self):
            return self.contents

        def _get_plain_body(self):
            return _strip_tags(self._get_html_body())

    email = SimpleHTMLMail(
        [appointment.participant.email],
        subject,
        contents,
    )
    email.send(connection=get_connection())


class Command(BaseCommand):
    help = "Sends email reminders before appointments, intended to be run as a cron job"

    def handle(self, *args, **options):
        # fetch appoinments 24 hours from now
        now = timezone.now()
        threshold_from = now + timedelta(days=1)
        threshold_to = threshold_from + timedelta(hours=1)

        appointments = Appointment.objects.filter(
            timeslot__start__gt=threshold_from, timeslot__start__lt=threshold_to, reminder_sent=None
        ).exclude(outcome=Appointment.Outcome.CANCELED)

        for appointment in appointments:
            try:
                log.info("Sending reminder, appointment %d", appointment.pk)
                send_reminder_mail(appointment, prepare_reminder_mail(appointment))
                appointment.reminder_sent = now
                appointment.save()
            except Exception:
                log.exception("Error sending reminder mail")
