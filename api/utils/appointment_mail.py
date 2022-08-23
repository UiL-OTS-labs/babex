import re
from typing import Optional

from django.conf import settings
from django.template import defaultfilters
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime
import urllib.parse as parse

from cdh.core.utils.mail import send_template_email

from experiments.models import Experiment, TimeSlot
from main.utils import get_supreme_admin
from participants.models import Participant

CANCEL_LINK_REGEX = r'{cancel_link(?::\"(.*)\")?}'


def send_appointment_mail(
        experiment: Experiment,
        participant: Participant,
        time_slot: Optional[TimeSlot],
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
        '{leader_phonenumber}': experiment.leader.phonenumber,
        '{all_leaders_name_list}': experiment.leader.name,
    }

    num_additional_leaders = experiment.additional_leaders.count()

    if num_additional_leaders > 0:
        last_leader = experiment.additional_leaders.last()
        assert last_leader is not None
        others = experiment.additional_leaders.exclude(pk=last_leader.pk)

        # If there's one additional, don't add the comma as it looks weird
        if num_additional_leaders > 1:
            replacements['{all_leaders_name_list}'] += ", "

        replacements['{all_leaders_name_list}'] += ", ".join(
            [x.name for x in others]
        )
        replacements['{all_leaders_name_list}'] += f" en {last_leader.name}"

    if experiment.location:
        replacements['{experiment_location}'] = experiment.location.name

    if experiment.use_timeslots and time_slot is not None:
        # We don't use strftime because that's not _always_ timezone aware
        # Also, using the template filter is a neat hack to have the same format
        # string syntax everywhere
        replacements.update({
            '{date}': defaultfilters.date(localtime(time_slot.datetime), 'l d-m-Y'),
            '{time}': defaultfilters.date(localtime(time_slot.datetime), 'H:i'),
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
