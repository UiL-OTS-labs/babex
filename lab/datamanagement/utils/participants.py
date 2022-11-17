from datetime import datetime

from typing import List, Tuple

from datamanagement.utils.common import get_threshold_years_ago
from participants.models import Participant
from auditlog.utils.log import log as log_to_auditlog
from auditlog.enums import Event, UserType


def get_participants_with_appointments() -> List[Tuple[Participant, datetime, int]]:
    out = []
    threshold = get_threshold_years_ago('participants_with_appointment')

    for participant in Participant.objects.filter(
        appointments__creation_date__lte=threshold,
    ).distinct():
        newest_appointment = participant.appointments.order_by(
            '-creation_date'
        ).first()

        assert newest_appointment is not None
        if newest_appointment.creation_date < threshold:
            out.append(
                (
                    participant,
                    newest_appointment.creation_date,
                    participant.appointments.count(),
                 )
            )

    return out


def get_participants_without_appointments() -> List[Participant]:
    return list(Participant.objects.filter(
        appointments=None,
        created__lte=get_threshold_years_ago('participants_without_appointment')
    ))


def delete_participant(participant: Participant, user) -> bool:
    if participant not in get_participants_without_appointments():
        return False

    log_to_auditlog(
        Event.DELETE_DATA,
        "Deleted participant '{}'".format(participant),
        user,
        UserType.ADMIN,
    )

    participant.delete()

    return True
