from datetime import datetime, timedelta

from cdh.core.mail import TemplateEmail
from cdh.core.utils.mail import send_template_email
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from comments.utils import add_system_comment
from experiments.models import Appointment
from main.utils import get_register_link


def cancel_appointment(appointment: Appointment) -> None:
    # Only handle late comment if there is a timeslot
    if appointment.timeslot:
        _handle_late_comment(appointment)
    _inform_leaders(appointment)
    _send_confirmation(appointment)

    appointment.cancel()


def _handle_late_comment(appointment: Appointment) -> None:
    """Helper function that adds a comment for this participant if he/she/it
    cancelled within 24 prior to the appointment.
    """
    if not appointment.timeslot:
        return

    dt = appointment.timeslot.datetime

    now = datetime.now(tz=dt.tzinfo)

    deadline = dt - timedelta(days=1)

    if now > deadline:
        add_system_comment(
            appointment.participant, "Cancelled less than 24h before experiment", appointment.timeslot.experiment
        )


def _inform_leaders(appointment: Appointment) -> None:
    experiment = appointment.experiment
    leaders = experiment.leaders.all()

    for leader in leaders:
        subject = "ILS participant deregistered for experiment: {}".format(experiment.name)
        context = {
            "appointment": appointment,
            "leader": leader,
        }

        mail = TemplateEmail(
            html_template="mail/appointment/canceled_leader.html",
            context=context,
            to=[leader.email],
            subject=subject,
        )
        mail.send()


def _send_confirmation(appointment: Appointment) -> None:
    context = {"appointment": appointment}

    mail = TemplateEmail(
        html_template="mail/appointment/canceled.html",
        context=context,
        to=[appointment.participant.email],
        subject=_("utils:cancel_appointment:subject"),
    )
    mail.send()
