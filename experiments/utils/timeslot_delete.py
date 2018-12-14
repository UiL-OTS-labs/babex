from .participant_subscription import unsubscribe_participant
from ..models import Experiment

_TIMESLOT_KEY_PREFIX = len("timeslot_")
_TIMESLOT_KEY_POSTFIX = len("[]")


def delete_timeslot(experiment: Experiment, timeslot_pk: int, to_delete: int=1) -> None:

    timeslot = experiment.timeslot_set.get(pk=timeslot_pk)

    places_left = timeslot.max_places - to_delete

    for place in timeslot.places[places_left:]:
        unsubscribe_participant(timeslot, place['participant'].pk)

    if places_left <= 0:
        timeslot.delete()
    else:
        timeslot.max_places = places_left
        timeslot.save()


def delete_timeslots(experiment: Experiment, post_data) -> None:
    for key in post_data.keys():
        if key.startswith('timeslot_'):
            timeslot = int(key[_TIMESLOT_KEY_PREFIX:-_TIMESLOT_KEY_POSTFIX])

            values = post_data.getlist(key)

            delete_timeslot(experiment, timeslot, len(values))

