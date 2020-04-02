from datetime import datetime

from typing import List, Tuple

from datamanagement.utils.common import get_threshold_years_ago
from participants.models import Participant

# TODO: participants who are in the systems but don't have any appointments


def get_old_participants() -> List[Tuple[Participant, datetime, int]]:
    out = []
    threshold = get_threshold_years_ago()

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
