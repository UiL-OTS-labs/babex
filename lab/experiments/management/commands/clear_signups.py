from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from signups.models import Signup


class Command(BaseCommand):
    help = "Removes processed signups, intended to be run as a cronjob"

    def handle(self, *args, **options):
        threshold = datetime.now() - timedelta(days=14)
        signups = Signup.objects.filter(created__lte=threshold).exclude(status=Signup.Status.NEW)
        count = signups.count()
        signups.delete()

        print(f"Removed {count} signups")
