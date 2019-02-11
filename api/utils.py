from datetime import datetime, timedelta

from django.conf import settings

from api.auth.models import ApiUser
from comments.models import Comment
from experiments.models import Appointment
from main.utils import get_supreme_admin, send_template_email
from participants.models import Participant


def send_password_reset_mail(user: ApiUser, token: str) -> None:
    link, alternative_link = get_reset_links(token)

    subject = 'UiL OTS Experimenten: password reset'
    context = {
        'token': token,
        'name': _get_name(user),
        'link': link,
        'alternative_link': alternative_link,
    }

    send_template_email(
        [user.email],
        subject,
        'api/mail/password_reset',
        context,
        'no-reply@uu.nl'
    )


def send_cancel_token_mail(participant: Participant, token: str,
                           email: str) -> None:
    link = "{}participant/appointments/{}/".format(settings.FRONTEND_URI, token)

    subject = 'UiL OTS Experimenten: afspraak afzeggen'
    context = {
        'token':            token,
        'name':             participant.name or 'proefpersoon',
        'link':             link,
    }

    send_template_email(
        [email],
        subject,
        'api/mail/cancel_token',
        context,
        'no-reply@uu.nl'
    )


def cancel_appointment(appointment: Appointment) -> None:
    _handle_late_comment(appointment)
    _inform_leaders(appointment)
    _send_confirmation(appointment)

    appointment.delete()


def _handle_late_comment(appointment: Appointment) -> None:
    """Helper function that adds a comment for this participant if he/she/it
    cancelled within 24 prior to the appointment.
    """
    dt = appointment.timeslot.datetime

    now = datetime.now(tz=dt.tzinfo)

    deadline = dt - timedelta(days=1)

    if now > deadline:
        comment = Comment()
        comment.participant = appointment.participant
        comment.comment = "Cancelled less than 24 before experiment"
        comment.experiment = appointment.timeslot.experiment
        comment.save()


def _inform_leaders(appointment: Appointment) -> None:
    experiment = appointment.timeslot.experiment

    leaders = [experiment.leader]
    if experiment.additional_leaders.exists():
        leaders.append(*experiment.additional_leaders.all())

    for leader in leaders:
        subject = 'UiL OTS participant deregistered for experiment: {}'.format(
            experiment.name)
        context = {
            'participant':     appointment.participant,
            'time_slot':       appointment.timeslot,
            'experiment':      experiment,
            'leader':          leader,
        }

        send_template_email(
            [leader.email],
            subject,
            'api/mail/participant_cancelled',
            context,
            'no-reply@uu.nl'
        )


def _send_confirmation(appointment: Appointment) -> None:
    admin = get_supreme_admin()
    experiment = appointment.timeslot.experiment
    time_slot = appointment.timeslot

    subject = 'UiL OTS uitschrijven experiment: {}'.format(experiment.name)
    context = {
        'participant':     appointment.participant,
        'time_slot':       time_slot,
        'experiment':      experiment,
        'admin':           admin.get_full_name(),
        'admin_email':     admin.email,
        'other_time_link': _get_resub_link(experiment.id),
        'home_link':       settings.FRONTEND_URI,
    }

    send_template_email(
        [appointment.participant.email],
        subject,
        'api/mail/cancelled_appointment',
        context,
        admin.email
    )


def _get_resub_link(experiment_id: int) -> str:
    return "{}participant/register/{}/".format(
        settings.FRONTEND_URI,
        experiment_id
    )


def _get_name(user: ApiUser):

    if hasattr(user, 'participant'):
        return user.participant.mail_name

    if hasattr(user, 'leader'):
        return user.leader.name

    return 'proefpersoon'


def get_reset_links(token: str):
    root = settings.FRONTEND_URI

    root = "{}reset_password/".format(root)

    complete = "{}{}/".format(root, token)

    return complete, root
