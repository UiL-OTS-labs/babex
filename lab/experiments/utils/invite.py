import re
import urllib.parse as parse
from typing import List

from cdh.core.utils.mail import send_personalised_mass_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from experiments.models import Experiment, Invitation
from main.models import User
from main.utils import get_register_link
from participants.models import Participant

link_to_subscribe_regex = r"{link_to_subscribe(?::\"(.*)\")?}"


def get_invite_mail_content(experiment: Experiment, leader: User) -> str:
    content = experiment.invite_email

    replacements = {
        "{duration}": experiment.duration,
        "{compensation}": experiment.compensation,
        "{task_description}": experiment.task_description,
        "{additional_instructions}": experiment.additional_instructions,
        "{experiment_name}": experiment.name,
        "{experiment_location}": "",
        "{leader_name}": leader.name,
        "{leader_email}": leader.email,
        "{leader_phonenumber}": leader.phonenumber,
        "{all_leaders_name_list}": experiment.leader_names,
    }

    if experiment.location:
        replacements["{experiment_location}"] = experiment.location.name

    for key, value in replacements.items():
        content = content.replace(key, value)

    return content


def mail_invite(participant_ids: List[str], content: str, experiment: Experiment) -> None:
    html_content = _parse_contents_html(content, experiment)
    plain_content = _parse_contents_plain(content, experiment)
    participants = Participant.objects.filter(pk__in=participant_ids)
    participants.prefetch_related()

    subject = "ILS uitnodiging deelname experiment: {}".format(experiment.name)

    # Generate the datatuple list for send_personalised_mass_mail
    # Please see that function's docstring for info
    data = [(subject, {"participant": participant}, [participant.email]) for participant in participants]

    # Technically html_content should be passed in a seperate html context,
    # but the plain context will just override content in the generic context
    # when rendering the plain text email. Thus, we can pass the html_content
    # in the regular context, as it will only be used in the html render.
    context = {"preview": False, "content": html_content, "reg_through_login_link": _get_login_exp_url(experiment)}

    plain_text_context = {"content": plain_content}

    send_personalised_mass_mail(data, "experiments/mail/invite", context, plain_context=plain_text_context)

    # Create a new invitation object for all participants, so we see a nice
    # checkbox
    Invitation.objects.bulk_create(
        [Invitation(experiment=experiment, participant=participant) for participant in participants if participant]
    )


def _get_login_exp_url(experiment: Experiment) -> str:
    return parse.urljoin(
        settings.FRONTEND_URI,
        "login/?next=/participant/register/{}/".format(
            experiment.pk,
        ),
    )


def _parse_contents_html(content: str, experiment: Experiment) -> str:
    match = re.search(link_to_subscribe_regex, content)

    if not match:
        return mark_safe(content)

    replacement = '<a href="{}">{}</a>'.format(get_register_link(experiment), match.group(1))

    return mark_safe(content.replace(match.group(0), replacement))


def _parse_contents_plain(content: str, experiment: Experiment) -> str:
    # Remove all HTML
    content = strip_tags(content)

    match = re.search(link_to_subscribe_regex, content)

    if not match:
        return mark_safe(content)

    replacement = "{} ({})".format(
        match.group(1),
        get_register_link(experiment),
    )

    return mark_safe(content.replace(match.group(0), replacement))
