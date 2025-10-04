import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from signups.models import Signup

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sends reminders, removes processed and expired signups. Intended to be run as a cronjob"

    def remove_processed(self):
        threshold = timezone.now() - timedelta(days=1)
        signups = Signup.objects.filter(created__lte=threshold).exclude(status=Signup.Status.NEW)
        count = signups.count()
        signups.delete()

        print(f"Removed {count} processed signups")

    def remove_expired(self):
        threshold = timezone.now() - timedelta(days=2)
        signups = Signup.objects.filter(created__lte=threshold, email_verified=None)
        count = signups.count()
        signups.delete()

        print(f"Removed {count} expired signups")

    def send_reminders(self):
        start = timezone.now() - timedelta(days=2)
        end = timezone.now() - timedelta(days=1)
        signups = Signup.objects.filter(created__gt=start, created__lte=end, reminder_sent=None, email_verified=None)
        count = signups.count()
        for signup in signups.all():
            signup.send_reminder()

        print(f"Sent {count} reminders")

    def handle(self, *args, **options):
        try:
            self.remove_processed()
        except:
            log.exception("Error removing processed signups")

        try:
            self.remove_expired()
        except:
            log.exception("Error removing expired signups")

        try:
            self.send_reminders()
        except:
            log.exception("Error sending reminders")
