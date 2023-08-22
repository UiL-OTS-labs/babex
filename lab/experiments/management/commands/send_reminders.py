from datetime import datetime, timedelta

from cdh.core.mail import TemplateEmail
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from experiments.models import Appointment


class Command(BaseCommand):
    help = "Sends email reminders before appointments, intended to be run as a cron job"

    def handle(self, *args, **options):
        # fetch appoinments 24 hours from now
        now = datetime.now()
        threshold = now + timedelta(days=1)

        appointments = Appointment.objects.filter(
            timeslot__start__gt=now, timeslot__start__lte=threshold, reminder_sent=None
        )

        for appointment in appointments:
            mail = TemplateEmail(
                html_template="experiments/mail/reminder.html",
                context=dict(
                    appointment=appointment,
                    base_url=settings.FRONTEND_URI,
                ),
                to=[appointment.participant.email],
                subject=_("experiments:mail:reminder:subject"),
            )

            appointment.reminder_sent = now
            appointment.save()
            mail.send()
