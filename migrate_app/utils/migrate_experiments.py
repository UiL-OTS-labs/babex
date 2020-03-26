from typing import Tuple, List, Dict

from django.db import connections

from participants.models import Participant
from ..models import Experiments as OldExperiment
from ..models import ExperimentsLeaders, Leaders as OldLeader
from ..models import ExperimentsExcluded, ExperimentsDefaultCriteria
from ..models import Criteria as OldCriterion, ExperimentsCriteria as \
    OldExperimentCriterion
from experiments.models import Criterion as NewCriterion, ExperimentCriterion\
    as NewExperimentCriterion
from experiments.models import Experiment as NewExperiment
from experiments.models import Location
from leaders.models import Leader
from ..defs import MIGRATE_LOCATION_NAME

from .migrate_timeslots import migrate_timeslots


def migrate_experiments(pp_mappings: Dict[int, Participant]) -> \
        Dict[int, NewExperiment]:
    experiment_pairs = _migrate_experiments()
    _migrate_other_experiment_exclusions(experiment_pairs)
    _migrate_default_criteria(experiment_pairs)
    _migrate_specific_criteria(experiment_pairs)

    migrate_timeslots(experiment_pairs, pp_mappings)

    return {old.pk: new for old, new in experiment_pairs}


def _migrate_experiments() -> List[Tuple[OldExperiment, NewExperiment]]:
    old_experiments = OldExperiment.objects.all()

    default_location = Location.objects.get(name=MIGRATE_LOCATION_NAME)

    out = []

    for old_experiment in old_experiments:  # type: OldExperiment
        if NewExperiment.objects.filter(name=old_experiment.name).exists():
            print("\nExperiment with name {} (pk {}) already exists in the new "
                  "DB! "
                  "Skipping...".format(old_experiment.name, old_experiment.pk))
            continue

        new_experiment = NewExperiment()
        new_experiment.name = old_experiment.name
        new_experiment.duration = old_experiment.duration
        new_experiment.compensation = old_experiment.compensation
        new_experiment.task_description = old_experiment.task_description
        new_experiment.additional_instructions = old_experiment.additional_instructions

        new_experiment.location = default_location
        new_experiment.default_max_places = old_experiment.places
        new_experiment.open = old_experiment.open == 1
        new_experiment.participants_visible = old_experiment.visible == 1

        old_leader = OldLeader.objects.get(
            pk=_get_leader_id_from_experiment(old_experiment)
        )
        new_leader = Leader.objects.get(api_user__email=old_leader.email)

        new_experiment.leader = new_leader

        new_experiment.save()

        out.append((old_experiment, new_experiment))

    return out


def _get_leader_id_from_experiment(experiment: OldExperiment) -> int:
    with connections['old'].cursor() as cursor:
        cursor.execute(
            "SELECT leader_id FROM experiments_leaders WHERE experiment_id = "
            "%s",
            [experiment.pk]
        )
        return cursor.fetchone()[0]


def _migrate_other_experiment_exclusions(
        experiment_pairs: List[Tuple[OldExperiment, NewExperiment]]
):
    for old_experiment, new_experiment in experiment_pairs:

        for exclusion_id in _get_exclusions_from_experiment(old_experiment):
            # Get the old experiment for this link
            old_excluded_experiment = OldExperiment.objects.get(
                pk=exclusion_id
            )

            # Get it's corresponding experiment in the new application
            new_excluded_experiment = NewExperiment.objects.get(
                name=old_excluded_experiment.name
            )

            # And exclude!
            new_experiment.excluded_experiments.add(new_excluded_experiment)

        new_experiment.save()


def _get_exclusions_from_experiment(experiment: OldExperiment) -> List[int]:
    with connections['old'].cursor() as cursor:
        cursor.execute(
            "SELECT experiment_ex_id FROM experiments_excluded WHERE "
            "experiment_id = %s",
            [experiment.pk]
        )
        return [int(x[0]) for x in cursor.fetchall()]


def _migrate_default_criteria(
        experiment_pairs: List[Tuple[OldExperiment, NewExperiment]]
):
    for old_experiment, new_experiment in experiment_pairs:
        old_crit = ExperimentsDefaultCriteria.objects.get(
            experiment_id=old_experiment.pk
        )

        # We don't need to create this, the application creates an instance
        # automatically when a new experiment is saved.
        new_crit = new_experiment.defaultcriteria

        if old_crit.language == 'indifferent':
            new_crit.language = "I"
        else:
            new_crit.language = old_crit.language

        new_crit.multilingual = _mapper(
            old_crit.multiple_lang,
            {
                'indifferent': 'I',
                'one': 'N',
                'many': 'Y',
            }
        )
        new_crit.sex = _mapper(
            old_crit.sex,
            {
                'M': 'M',
                'F': 'F',
                'indifferent': 'I'
            }
        )
        new_crit.handedness = _mapper(
            old_crit.handedness,
            {
                'right': 'R',
                'left': 'L',
                'indifferent': 'I'
            }
        )
        new_crit.dyslexia = _mapper(
            old_crit.dyslectic,
            {
                'yes': 'Y',
                'no': 'N',
                'indifferent': 'N'  # Indifferent is not supported anymore
            }
        )
        new_crit.social_status = _mapper(
            old_crit.social_role,
            {
                'student': 'S',
                'indifferent': 'I',
                # There are more options, but these two are the only ones that
                # are present in the DB as of 2019-11-05
            }
        )

        # Fix the weird ass age criteria from the old application
        min_age = -1
        max_age = -1

        if old_crit.type_age == 'older_than':
            try:
                min_age = int(old_crit.age)
            except ValueError:
                raise Exception(
                    'Malformed min_age found! Experiment pk {},{}'.format(
                        old_experiment.pk,
                        new_experiment.pk
                    )
                )
        elif old_crit.type_age == 'younger_than':
            try:
                max_age = int(old_crit.age)
            except ValueError:
                raise Exception(
                    'Malformed max_age found! Experiment pk {},{}'.format(
                        old_experiment.pk,
                        new_experiment.pk
                    )
                )
        elif old_crit.type_age == 'between':
            try:
                min_age, max_age = old_crit.age.split(',')
                min_age = int(min_age)
                max_age = int(max_age)
            except ValueError:
                raise Exception(
                    'Malformed min_age/max_age found! Experiment pk {},'
                    '{}'.format(
                        old_experiment.pk,
                        new_experiment.pk
                    )
                )

        new_crit.min_age = min_age
        new_crit.max_age = max_age


def _migrate_specific_criteria(
        experiment_pairs: List[Tuple[OldExperiment, NewExperiment]]
):
    for old_experiment, new_experiment in experiment_pairs:

        for old_crit in _get_criteria_from_experiment(old_experiment):

            new_crit = _get_new_crit(old_crit)

            new_coupling = NewExperimentCriterion()
            new_coupling.experiment = new_experiment
            new_coupling.criterion = new_crit
            new_coupling.correct_value = old_crit.value_correct
            new_coupling.message_failed = old_crit.message_failed
            new_coupling.save()


def _get_criteria_from_experiment(experiment: OldExperiment) -> List[OldCriterion]:
    with connections['old'].cursor() as cursor:
        cursor.execute(
            "SELECT criteria_id FROM experiments_criteria WHERE "
            "experiment_id = %s",
            [experiment.pk]
        )
        return [OldCriterion.objects.get(pk=int(x[0])) for x in
                                         cursor.fetchall()]


def _get_new_crit(old_crit: OldCriterion):
    qs = NewCriterion.objects.filter(
        name_form=old_crit.name_form,
        name_natural=old_crit.name_natural,
        values=old_crit.values,
    )

    if qs.exists():
        return qs.get()
    else:
        return NewCriterion.objects.create(
            name_form=old_crit.name_form,
            name_natural=old_crit.name_natural,
            values=old_crit.values,
        )


def _mapper(val: str, mappings: dict) -> str:
    for old, new in mappings.items():
        if val.lower() == old.lower():
            return new

    raise Exception(
        "Unknown value '{}' supplied in _mapper. Mappings: {}".format(val, mappings)
    )
