import re
from typing import List

from django.conf import settings
from django.utils.safestring import mark_safe

from experiments.models import Experiment, Invitation
from main.utils import get_supreme_admin, send_personalised_mass_mail
from participants.models import Participant

link_to_subscribe_regex = r'{link_to_subscribe(?::\"(.*)\")?}'


def mail_invite(
        participant_ids: List[str],
        content: str,
        experiment: Experiment) -> None:
    admin = get_supreme_admin()
    content = parse_contents(content, experiment)
    participants = Participant.objects.filter(pk__in=participant_ids)

    subject = 'UiL OTS uitnodiging deelname experiment: {}'.format(
        experiment.name
    )

    # Generate the datatuple list for send_personalised_mass_mail
    # Please see that function's docstring for info
    data = [(subject, {'participant': participant}, [participant.email]) for
            participant in participants]

    context = {
        'preview': False,
        'content': content,
        'unsub_link': "{}participant/cancel/".format(settings.FRONTEND_URI)
    }

    send_personalised_mass_mail(
        data,
        'experiments/mail/invite',
        context,
        admin.email
    )

    # Create a new invitation object for all participants, so we see a nice
    # checkbox
    Invitation.objects.bulk_create(
        [Invitation(experiment=experiment, participant=participant) for
         participant in participants]
    )


def _get_exp_url(experiment) -> str:
    return "{}participant/register/{}/".format(
        settings.FRONTEND_URI,
        experiment.id,
    )


def parse_contents(content: str, experiment: Experiment) -> str:
    match = re.search(link_to_subscribe_regex, content)

    if not match:
        return content

    replacement = "<a href=\"{}\">{}</a>".format(
        _get_exp_url(experiment),
        match.group(1)
    )

    return mark_safe(content.replace(match.group(0), replacement))
