from datetime import datetime

from typing import List, Tuple

from datamanagement.utils.common import get_threshold_years_ago
from participants.models import Participant


def get_participants_with_appointments() -> List[Tuple[Participant, datetime, int]]:
    out = []
    threshold = get_threshold_years_ago('participants_with_appointment')

    for participant in Participant.objects.filter(
        appointments__timeslot__datetime__lte=threshold
    ).distinct():
        newest_appointment = participant.appointments.order_by(
            '-timeslot__datetime'
        ).first()

        print(newest_appointment)

        if newest_appointment.timeslot.datetime < threshold:
            out.append(
                (
                    participant,
                    newest_appointment.timeslot.datetime,
                    participant.appointments.count(),
                 )
            )

    return out


def get_participants_without_appointments() -> List[Participant]:
    return list(Participant.objects.filter(
        appointments=None,
        created__lte=get_threshold_years_ago('participants_without_appointment')
    ))
