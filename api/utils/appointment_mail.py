import re

from django.conf import settings
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
import urllib.parse as parse

from experiments.models import Experiment, TimeSlot
from main.utils import get_supreme_admin, send_template_email
from participants.models import Participant

CANCEL_LINK_REGEX = r'{cancel_link(?::\"(.*)\")?}'


def send_appointment_mail(
        experiment: Experiment,
        participant: Participant,
        time_slot: TimeSlot,
) -> None:
    admin = get_supreme_admin()
    template = 'api/mail/new_appointment'

    subject = 'Bevestiging inschrijving experiment UiL OTS: {}'.format(
        experiment.name
    )

    replacements = {
        '{experiment_name}': experiment.name,
        '{experiment_location}': '',
        '{participant_name}': participant.name,
        '{leader_name}': experiment.leader.name,
        '{leader_email}': experiment.leader.api_user.email,
        '{leader_phonenumber}': experiment.leader.phonenumber
    }

    if experiment.location:
        replacements['{experiment_location}'] = experiment.location.name

    if experiment.use_timeslots:
        replacements.update({
            '{date}': time_slot.datetime.strftime('%d-%m-%Y'),
            '{time}': time_slot.datetime.strftime('%-H:%I'),
        })

    send_template_email(
        [participant.email],
        subject,
        template,
        {
            'experiment': experiment,
            'html_content': _parse_contents_html(
                experiment.confirmation_email,
                replacements
            ),
            'plain_content': _parse_contents_plain(
                experiment.confirmation_email,
                replacements
            )
        },
        admin.email
    )


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

