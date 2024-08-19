from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from mailauth.models import MailAuth


class Command(BaseCommand):
    help = "Removes old mail auth sessions, intended to be run as a cronjob"

    def handle(self, *args, **options):
        threshold = datetime.now() - timedelta(days=14)
        MailAuth.objects.filter(expiry__lte=threshold).delete()
