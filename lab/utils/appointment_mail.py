import re
import urllib.parse as parse

from cdh.core.mail.classes import BaseEmail, _strip_tags
from django.conf import settings
from django.core.mail import get_connection
from django.template import defaultfilters
from django.utils import translation
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime

from experiments.email import AppointmentConfirmEmail
from experiments.models import Appointment
from mailauth.models import create_mail_auth

CANCEL_LINK_REGEX = r"{cancel_link(?::\"(.*)\")?}"


def prepare_appointment_mail(appointment: Appointment):
    experiment = appointment.experiment
    participant = appointment.participant
    time_slot = appointment.timeslot
    assert time_slot

    # generate auth link for cancelation
    expiry = time_slot.end
    mauth = create_mail_auth(expiry, participant=appointment.participant)

    cancel_link = mauth.get_link(f"/appointment/{appointment.pk}/cancel/")

    # override locale to force dates to use Dutch weekdays
    with translation.override("nl"):
        replacements = {
            "experiment_name": experiment.name,
            "experiment_location": "",
            "participant_name": participant.name,
            "parent_name": participant.parent_name,
            "leader_name": appointment.leader.name,
            "leader_email": appointment.leader.email,
            "leader_phonenumber": appointment.leader.phonenumber,
            "all_leaders_name_list": experiment.leader_names,
            "cancel_link": cancel_link,
            "date": defaultfilters.date(localtime(time_slot.start), "l d-m-Y"),
            "time": defaultfilters.date(localtime(time_slot.start), "H:i"),
        }

    if experiment.location:
        replacements["experiment_location"] = experiment.location.name

    subject = "Bevestiging inschrijving experiment ILS: {}".format(appointment.experiment.name)
    email = AppointmentConfirmEmail(
        [participant.email],
        subject,
        contents=experiment.confirmation_email,
        attachments=[(f.filename, f.file.read(), f.file.content_type) for f in experiment.attachments.all()],
    )
    email.context = replacements
    return email._get_html_body()


def send_appointment_mail(appointment: Appointment, contents: str) -> None:
    subject = "Bevestiging inschrijving experiment ILS: {}".format(appointment.experiment.name)

    class SimpleHTMLMail(BaseEmail):
        def __init__(self, to, subject, contents):
            super().__init__(to, subject)
            self.contents = contents

        def _get_html_context(self):
            return dict()

        def _get_html_body(self):
            return self.contents

        def _get_plain_body(self):
            return _strip_tags(self._get_html_body())

    email = SimpleHTMLMail([appointment.participant.email], subject, contents)
    email.send(connection=get_connection())


def _parse_contents_html(
    content: str,
    replacements: dict,
) -> str:
    match = re.search(CANCEL_LINK_REGEX, content)

    if match:
        replacement = '<a href="{}">{}</a>'.format(
            parse.urljoin(settings.FRONTEND_URI, "participant/cancel/"), match.group(1)
        )
        content = content.replace(match.group(0), replacement)

    content = _apply_replacements(content, replacements)

    return mark_safe(content)


def _parse_contents_plain(
    content: str,
    replacements: dict,
) -> str:
    # Remove all HTML
    content = strip_tags(content)

    match = re.search(CANCEL_LINK_REGEX, content)

    if match:
        replacement = "{} ({})".format(
            match.group(1),
            parse.urljoin(settings.FRONTEND_URI, "participant/cancel/"),
        )
        content = content.replace(match.group(0), replacement)

    content = _apply_replacements(content, replacements)

    return mark_safe(content)


def _apply_replacements(content: str, replacements: dict) -> str:
    for key, value in replacements.items():
        content = content.replace(key, value)

    return content
