from datetime import datetime
from typing import List, Union


from experiments.models import Experiment, TimeSlot


def add_timeslot(
        experiment: Experiment,
        date_time: Union[str, datetime],
        places: int) -> TimeSlot:

    existing = TimeSlot.objects.filter(
        datetime=date_time,
        experiment=experiment
    )

    if existing:
        return _add_to_existing_timeslot(existing, places)
    else:
        return _create_new_timeslot(experiment, date_time, places)


def _merge_existing_timeslots(existing: List[TimeSlot]):
    """This function merges a list of TimeSlots into one.
    It does this by taking the first slot, and looping over the rest.

    Each slot in 'rest' will have it's max_slots added to 'first', and it's
    appointments are also moved to 'first'
    """
    # Split the list into [H|r] (Prolog notation)
    first = existing[0]
    rest = existing[1:]

    for slot in rest:
        # Add the slots to the first slot
        first.max_places = first.max_places + slot.max_places
        # Move appointments
        for appointment in slot.appointments.all():
            appointment.timeslot = first
            appointment.save()

        # Remove the now-empty slot
        slot.delete()

    first.save()

    return first


def _add_to_existing_timeslot(existing: List[TimeSlot],
                              places: int) -> TimeSlot:
    if len(existing) > 1:
        existing = _merge_existing_timeslots(existing)
    else:
        existing = existing[0]

    existing.max_places = existing.max_places + places

    existing.save()

    return existing


def _create_new_timeslot(experiment: Experiment, date_time: datetime,
                         places: int) -> TimeSlot:
    time_slot = TimeSlot()

    time_slot.experiment = experiment
    time_slot.max_places = places
    time_slot.datetime = date_time

    time_slot.save()

    return time_slot
