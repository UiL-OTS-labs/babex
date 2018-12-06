from ..models import Experiment


def delete_timeslot(experiment: Experiment, timeslot_pk: int, to_delete: int=1) -> None:

    timeslot = experiment.timeslot_set.get(pk=timeslot_pk)

    places_left = timeslot.max_places - to_delete

    if places_left <= 0:
        timeslot.delete()
    else:
        timeslot.max_places = places_left
        timeslot.save()


def delete_timeslots(experiment: Experiment, post_data) -> None:
    for key in post_data.keys():
        if key.startswith('timeslot_'):
            timeslot = key.replace('timeslot_', '')
            timeslot = timeslot.replace('[]', '')
            timeslot = int(timeslot)

            values = post_data.getlist(key)

            delete_timeslot(experiment, timeslot, len(values))

# TODO handle deleting slots with participants
