from django.conf import settings
from django.contrib.auth import get_user_model
from cdh.core.utils.mail import send_template_email

import auditlog.utils.log as auditlog
from auditlog.enums import Event, UserType
from experiments.models import Appointment
from main.utils import get_register_link


def unsubscribe_participant(appointment_pk: int,
                            sent_email: bool = True,
                            deleting_user=None) -> None:
    appointment = Appointment.objects.get(pk=appointment_pk)
    time_slot = appointment.timeslot
    experiment = appointment.experiment

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
        subject = 'UiL OTS uitschrijven experiment: {}'.format(experiment.name)
        context = {
            'participant':     appointment.participant,
            'time_slot':       time_slot,
            'experiment':      experiment,
            'admin':           appointment.leader.user.get_full_name(),
            'admin_email':     appointment.leader.email,
            'other_time_link': get_register_link(experiment),
            'home_link':       settings.FRONTEND_URI,
        }

        send_template_email(
            [appointment.participant.email],
            subject,
            'timeslots/mail/unsubscribed',
            context
        )


def _log_deletions(message, deleting_user):
    user_type = UserType.UNKNOWN

    # Determine user_type from deleting_user
    if isinstance(deleting_user, get_user_model()):
        user_type = UserType.ADMIN

    auditlog.log(
        Event.DELETE_DATA,
        message,
        deleting_user,
        user_type,
    )
