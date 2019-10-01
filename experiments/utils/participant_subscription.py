from experiments.models import Appointment, Experiment
from main.utils import get_supreme_admin, send_template_email
from django.conf import settings
from auditlog.enums import Event, UserType
import auditlog.utils.log as auditlog
from django.contrib.auth import get_user_model
from api.auth.models import ApiUser


def unsubscribe_participant(appointment_pk: int,
                            sent_email: bool = True,
                            deleting_user=None) -> None:
    appointment = Appointment.objects.get(pk=appointment_pk)
    time_slot = appointment.timeslot
    experiment = time_slot.experiment

    # Always delete first, the data in it will still be available for the
    # next bit
    appointment.delete()

    message = "User deleted appointment for experiment '{}' for " \
              "participant '{} ({})'".format(
        experiment.name,
        appointment.participant.fullname,
        appointment.participant.pk,
    )

    _log_deletions(message, deleting_user)

    if sent_email:
        admin = get_supreme_admin()

        subject = 'UiL OTS uitschrijven experiment: {}'.format(experiment.name)
        context = {
            'participant':     appointment.participant,
            'time_slot':       time_slot,
            'experiment':      experiment,
            'admin':           admin.get_full_name(),
            'admin_email':     admin.email,
            'other_time_link': _get_other_time_link(experiment),
            'home_link':       settings.FRONTEND_URI,
        }

        send_template_email(
            [appointment.participant.email],
            subject,
            'timeslots/mail/unsubscribed',
            context,
            admin.email
        )


def _log_deletions(message, deleting_user):
    user_type = UserType.UNKNOWN

    # Determine user_type from deleting_user
    if isinstance(deleting_user, get_user_model()):
        user_type = UserType.ADMIN
    elif isinstance(deleting_user, ApiUser):
        user_type = UserType.LEADER

    auditlog.log(
        Event.DELETE_DATA,
        message,
        deleting_user,
        user_type,
    )


def _get_other_time_link(experiment: Experiment) -> str:
    return "{}participant/register/{}/".format(
        settings.FRONTEND_URI,
        experiment.pk
    )
