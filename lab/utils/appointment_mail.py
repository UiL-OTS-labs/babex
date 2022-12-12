import re

from django.conf import settings
from django.core.mail import get_connection
from django.template import defaultfilters
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime
import urllib.parse as parse

from experiments.email import AppointmentConfirmEmail
from experiments.models import Appointment

CANCEL_LINK_REGEX = r'{cancel_link(?::\"(.*)\")?}'


def send_appointment_mail(appointment: Appointment, override_content=None) -> None:
    experiment = appointment.experiment
    participant = appointment.participant
    time_slot = appointment.timeslot

    subject = 'Bevestiging inschrijving experiment UiL OTS: {}'.format(
        experiment.name
    )

    replacements = {
        '{experiment_name}': experiment.name,
        '{experiment_location}': '',
        '{participant_name}': participant.name,
        '{leader_name}': appointment.leader.name,
        '{leader_email}': appointment.leader.user.email,
        '{leader_phonenumber}': appointment.leader.phonenumber,
        '{all_leaders_name_list}': experiment.leader_names
    }

    if experiment.location:
        replacements['experiment_location'] = experiment.location.name

    if experiment.use_timeslots and time_slot is not None:
        # We don't use strftime because that's not _always_ timezone aware
        # Also, using the template filter is a neat hack to have the same format
        # string syntax everywhere
        replacements.update({
            'date': defaultfilters.date(localtime(time_slot.start), 'l d-m-Y'),
            'time': defaultfilters.date(localtime(time_slot.start), 'H:i'),
        })

    email = AppointmentConfirmEmail(
        [participant.email], subject, contents=override_content or experiment.confirmation_email)
    email.context = replacements
    email.send(connection=get_connection())


def _parse_contents_html(
        content: str,
        replacements: dict,
) -> str:
    match = re.search(CANCEL_LINK_REGEX, content)

    if match:
        replacement = "<a href=\"{}\">{}</a>".format(
            parse.urljoin(settings.FRONTEND_URI, 'participant/cancel/'),
            match.group(1)
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
            parse.urljoin(settings.FRONTEND_URI, 'participant/cancel/'),
        )
        content = content.replace(match.group(0), replacement)

    content = _apply_replacements(content, replacements)

    return mark_safe(content)


def _apply_replacements(content: str, replacements: dict) -> str:

    for key, value in replacements.items():
        content = content.replace(key, value)

    return content
