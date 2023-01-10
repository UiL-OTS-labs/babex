import urllib.parse as parse

from django.conf import settings
from cdh.core.utils.mail import send_template_email

from experiments.models import Appointment


def remind_participant(appointment: Appointment) -> None:
    experiment = appointment.experiment

    subject = 'UiL OTS *Reminder* opgave experiment: {}'.format(experiment.name)
    context = {
        'participant':     appointment.participant,
        'leader':          appointment.leader,
        'time_slot':       appointment.timeslot,
        'experiment':      experiment,
        'cancel_link':     _make_cancel_link()
    }

    send_template_email(
        [appointment.participant.email],
        subject,
        'experiments/mail/reminder',
        context
    )


def _make_cancel_link() -> str:
    return parse.urljoin(
        settings.FRONTEND_URI,
        "participant/cancel/"
    )
