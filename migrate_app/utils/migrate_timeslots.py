from typing import Tuple, List, Dict, Optional
from datetime import datetime

from django.db import connections
import pytz

from participants.models import Participant
from ..models import Experiments as OldExperiment
from ..models import ExperimentsTimeslots as OldExperimentTimeslots
from ..models import Timeslots as OldTimeslot, ParticipantsTimeslots as \
    OldParticipantTimeslots
from experiments.models import Experiment as NewExperiment
from experiments.models import TimeSlot as NewTimeslot, Appointment as \
    NewAppointment


def migrate_timeslots(
        experiment_pairs: List[Tuple[OldExperiment, NewExperiment]],
        pp_mappings: Dict[int, Participant]
):

    for old_experiment, new_experiment in experiment_pairs:

        old_parsed = {}

        for old_timeslot in _get_timeslots_from_experiment(old_experiment):
            if old_timeslot.tdate not in old_parsed:
                old_parsed[old_timeslot.tdate] = {}

            if old_timeslot.ttime not in old_parsed[old_timeslot.tdate]:
                old_parsed[old_timeslot.tdate][old_timeslot.ttime] = []

            old_parsed[old_timeslot.tdate][old_timeslot.ttime].append(old_timeslot)

        for day, times in old_parsed.items():
            for time, slots in times.items():
                dt = datetime.combine(
                    day,
                    time,
                    tzinfo=pytz.timezone("Europe/Amsterdam")
                )

                new_slot = NewTimeslot()
                new_slot.experiment = new_experiment
                new_slot.datetime = dt
                new_slot.max_places = len(slots)
                new_slot.save()

                migrate_appointments(slots, new_slot, pp_mappings)


def _get_timeslots_from_experiment(experiment: OldExperiment) -> List[
    OldTimeslot]:
    with connections['old'].cursor() as cursor:
        cursor.execute(
            "SELECT timeslot_id FROM experiments_timeslots WHERE "
            "experiment_id = %s",
            [experiment.pk]
        )
        return [OldTimeslot.objects.get(pk=int(x[0])) for x in
                                         cursor.fetchall()]


def migrate_appointments(
        old_slots: List[OldTimeslot],
        new_slot: NewTimeslot,
        pp_mappings: Dict[int, Participant]
):
    for old_slot in old_slots:
        opp = _get_participant_from_timeslot(old_slot)

        if not opp:
            continue

        new_participant_pk = pp_mappings[opp]

        new_appointment = NewAppointment()
        new_appointment.participant = new_participant_pk
        new_appointment.timeslot = new_slot
        new_appointment.experiment = new_slot.experiment
        new_appointment.save()


def _get_participant_from_timeslot(timeslot: OldTimeslot) -> Optional[int]:
    with connections['old'].cursor() as cursor:
        cursor.execute(
            "SELECT participant_id FROM participants_timeslots WHERE "
            "timeslot_id = %s",
            [timeslot.pk]
        )
        row = cursor.fetchone()
        if row:
            return int(row[0])
        else:
            return None
