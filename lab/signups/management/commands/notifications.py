from datetime import datetime, timedelta

from cdh.mail.classes import TemplateEmail
from django.conf import settings
from django.core.management.base import BaseCommand

from main.models import User
from signups.models import Signup


class Command(BaseCommand):
    help = "Sends notifications about new signups, intended to be run as a cronjob"

    def handle(self, *args, **options):
        # fetch new signups from the last 7 days
        threshold = datetime.now() - timedelta(days=7)
        new_signups = Signup.objects.filter(status=Signup.Status.NEW, created__gte=threshold).count()
        total_waiting = Signup.objects.filter(status=Signup.Status.NEW).exclude(email_verified=None).count()
        unverified = Signup.objects.filter(status=Signup.Status.NEW, email_verified=None).count()

        # mail should reach all lab managers
        recipients = User.objects.filter(is_staff=True)
        if new_signups > 0:
            mail = TemplateEmail(
                html_template="signups/mail/notification.html",
                context=dict(
                    count=new_signups,
                    total=total_waiting,
                    unverified=unverified,
                    base_url=settings.FRONTEND_URI,
                ),
                to=[],
                bcc=recipients.values_list("email", flat=True),
                subject="Babex: new signups",
            )

            mail.send()
