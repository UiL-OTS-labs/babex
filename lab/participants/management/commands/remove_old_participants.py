from datetime import datetime

from ageutil import date_of_birth
from cdh.mail.classes import TemplateEmail
from django.core.management.base import BaseCommand
from django.utils import translation
from django.utils.translation import gettext

from participants.models import Participant


class Command(BaseCommand):
    help = "Removes processed signups, intended to be run as a cronjob"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            help="Dry run: only print information without removing participants",
            action="store_true",
            default=False,
        )

    def handle(self, *args, **options):
        participants = Participant.objects.filter(deactivated=None)

        to_remove = []  # participants that are older than the standard limit
        to_remove_longer = []  # participants that are older than 10 years

        for p in participants:
            y, m, _ = p.age
            if y >= 10:
                to_remove_longer.append(p)
            elif (y >= 2 and m > 6) or y >= 3:
                if not p.save_longer:
                    to_remove.append(p)

        if not options["dry_run"]:
            for p in to_remove:
                email = p.email
                p.deactivate(send_mail=False)
                # send standard mail
                with translation.override("nl"):
                    mail = TemplateEmail(
                        html_template="mail/removed_standard_limit.html",
                        to=[email],
                        subject=gettext("participants:remove_old:mail:subject"),
                    )
                    mail.send()
            for p in to_remove_longer:
                email = p.email
                p.deactivate(send_mail=False)
                # send 10 year mail
                with translation.override("nl"):
                    mail = TemplateEmail(
                        html_template="mail/removed_longer_limit.html",
                        to=[email],
                        subject=gettext("participants:remove_old:mail:subject"),
                    )
                    mail.send()

        count = len(to_remove + to_remove_longer)
        print(f"Deactivated {count} participants")
