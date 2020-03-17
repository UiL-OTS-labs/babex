from typing import Tuple, List
from datetime import datetime

from ..models import Experiments as OldExperiment
from ..models import ExperimentsTimeslots as OldExperimentTimeslots
from ..models import Timeslots as OldTimeslot
from experiments.models import Experiment as NewExperiment
from experiments.models import TimeSlot as NewTimeslot


def migrate_timeslots(experiment_pairs: List[Tuple[OldExperiment,
                                                   NewExperiment]]):

    for old_experiment, new_experiment in experiment_pairs:

        old_timeslot_coupling = OldExperimentTimeslots.objects.filter(
            experiment_id=old_experiment.pk
        )

        old_timeslots = [OldTimeslot.objects.get(pk=timeslot.id) for timeslot
                         in old_timeslot_coupling]

        old_parsed = {}

        for old_timeslot in old_timeslots:
            if old_timeslot.tdate not in old_parsed:
                old_parsed[old_timeslot.tdate] = {}

            if old_timeslot.ttime not in old_parsed[old_timeslot.tdate]:
                old_parsed[old_timeslot.tdate][old_timeslot.ttime] = []

            old_parsed[old_timeslot.tdate][old_timeslot.ttime].append(old_timeslot)

        for day, times in old_parsed.values():
            for time, slots in times.values():
                dt = datetime.combine(day, time)

                new_slot = NewTimeslot()
                new_slot.experiment = new_experiment
                new_slot.datetime = dt
                new_slot.max_places = len(slots)
                new_slot.save()