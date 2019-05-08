from django.conf import settings

from experiments.models import Appointment
from main.utils import get_supreme_admin, send_template_email


def remind_participant(appointment: Appointment) -> None:
    experiment = appointment.timeslot.experiment
    admin = get_supreme_admin()

    subject = 'UiL OTS *Reminder* opgave experiment: {}'.format(experiment.name)
    context = {
        'participant':     appointment.participant,
        'time_slot':       appointment.timeslot,
        'experiment':      experiment,
        'cancel_link':     "{}participant/cancel/".format(settings.FRONTEND_URI)
    }

    send_template_email(
        [appointment.participant.email],
        subject,
        'experiments/mail/reminder',
        context,
        admin.email
    )
