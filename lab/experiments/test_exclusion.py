from datetime import datetime, timedelta

from experiments.models import DefaultCriteria, TimeSlot
from experiments.utils.exclusion import get_eligible_participants_for_experiment
from participants.models import Participant, ParticipantData, Language


def test_excluded_experiment(admin_user, sample_participant):
    experiment_1 = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create())
    experiment_2 = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create())
    experiment_3 = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create())

    # mark participant as having participated in experiment #1
    timeslot = TimeSlot.objects.create(
        start=datetime.now() + timedelta(hours=24),
        end=datetime.now() + timedelta(hours=25),
        experiment=experiment_1,
    )
    sample_participant.appointments.create(experiment=experiment_1, leader=admin_user, timeslot=timeslot)

    assert sample_participant in get_eligible_participants_for_experiment(experiment_2)

    # cannot participat in #3 if participated in #1
    experiment_3.excluded_experiments.add(experiment_1)

    assert sample_participant not in get_eligible_participants_for_experiment(experiment_3)


def test_required_experiment(admin_user, sample_participant):
    experiment_1 = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create())
    experiment_2 = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create())

    # cannot participat in #2 unless participated in #1
    experiment_2.required_experiments.add(experiment_1)

    assert sample_participant not in get_eligible_participants_for_experiment(experiment_2)

    # mark participant as having participated in experiment #1
    # create a test appointment
    timeslot = TimeSlot.objects.create(
        start=datetime.now() + timedelta(hours=24),
        end=datetime.now() + timedelta(hours=25),
        experiment=experiment_1,
    )
    sample_participant.appointments.create(experiment=experiment_1, leader=admin_user, timeslot=timeslot)

    assert sample_participant in get_eligible_participants_for_experiment(experiment_2)


def test_required_experiment_multiple(admin_user, sample_participant):
    experiment_1 = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create())
    experiment_2 = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create())
    experiment_3 = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create())

    # cannot participat in #3 unless participated in #1 and #2
    experiment_3.required_experiments.add(experiment_1)
    experiment_3.required_experiments.add(experiment_2)

    assert sample_participant not in get_eligible_participants_for_experiment(experiment_3)

    timeslot = TimeSlot.objects.create(
        start=datetime.now() + timedelta(hours=24),
        end=datetime.now() + timedelta(hours=25),
        experiment=experiment_1,
    )
    sample_participant.appointments.create(experiment=experiment_1, leader=admin_user, timeslot=timeslot)
    timeslot = TimeSlot.objects.create(
        start=datetime.now() + timedelta(hours=48),
        end=datetime.now() + timedelta(hours=49),
        experiment=experiment_2,
    )
    sample_participant.appointments.create(experiment=experiment_2, leader=admin_user, timeslot=timeslot)

    assert sample_participant in get_eligible_participants_for_experiment(experiment_3)


def set_participant_field(participant, field_name, value):
    ParticipantData.objects.filter(pk=participant.data.pk).update(**{field_name: value})


def test_parent_criterion_required(admin_user, sample_participant):
    for criterion in ["dyslexic_parent", "tos_parent"]:
        experiment = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create(**{criterion: "Y"}))
        for value in [Participant.WhichParent.FEMALE, Participant.WhichParent.MALE, Participant.WhichParent.BOTH]:
            set_participant_field(sample_participant, criterion, value)
            assert sample_participant in get_eligible_participants_for_experiment(
                experiment
            ), f"Participant with field {criterion} set to {value} is missing from eligible set"
        for value in [Participant.WhichParent.NEITHER, Participant.WhichParent.UNKNOWN]:
            set_participant_field(sample_participant, criterion, value)
            assert sample_participant not in get_eligible_participants_for_experiment(
                experiment
            ), f"Participant with field {criterion} set to {value} is present in eligible set"


def test_parent_criterion_excluded(admin_user, sample_participant):
    for criterion in ["dyslexic_parent", "tos_parent"]:
        experiment = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create(**{criterion: "N"}))
        for value in [
            Participant.WhichParent.FEMALE,
            Participant.WhichParent.MALE,
            Participant.WhichParent.BOTH,
            Participant.WhichParent.UNKNOWN,
        ]:
            set_participant_field(sample_participant, criterion, value)
            assert sample_participant not in get_eligible_participants_for_experiment(experiment)
        for value in [Participant.WhichParent.NEITHER]:
            set_participant_field(sample_participant, criterion, value)
            assert sample_participant in get_eligible_participants_for_experiment(experiment)


def test_parent_criterion_indifferent(admin_user, sample_participant):
    for criterion in ["dyslexic_parent", "tos_parent"]:
        experiment = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create())
        for value in [choice[0] for choice in Participant.WhichParent.choices]:
            set_participant_field(sample_participant, criterion, value)
            assert sample_participant in get_eligible_participants_for_experiment(
                experiment
            ), f"Participant with field {criterion} set to {value} is missing from eligible set"

        experiment = admin_user.experiments.create(
            defaultcriteria=DefaultCriteria.objects.create(**{criterion: ["Y", "N"]})
        )
        for value in [choice[0] for choice in Participant.WhichParent.choices]:
            set_participant_field(sample_participant, criterion, value)
            assert sample_participant in get_eligible_participants_for_experiment(
                experiment
            ), f"Participant with field {criterion} set to {value} is missing from eligible set"


def test_participant_criteria(admin_user, sample_participant):
    criteria = ["sex", "birth_weight", "pregnancy_duration"]
    for criterion_name in criteria:
        options = set(x[0] for x in getattr(DefaultCriteria, criterion_name).field.options)
        for option in options:
            set_participant_field(sample_participant, criterion_name, option)

            # indifferent
            experiment = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create())
            assert sample_participant in get_eligible_participants_for_experiment(
                experiment
            ), f"Participant with field {criterion_name} set to {option} is missing from eligible set"

            # included
            experiment = admin_user.experiments.create(
                defaultcriteria=DefaultCriteria.objects.create(**{criterion_name: [option]})
            )
            assert sample_participant in get_eligible_participants_for_experiment(
                experiment
            ), f"Participant with field {criterion_name} set to {option} is missing from eligible set"

            # excluded
            experiment = admin_user.experiments.create(
                defaultcriteria=DefaultCriteria.objects.create(**{criterion_name: list(options - set([option]))})
            )
            assert sample_participant not in get_eligible_participants_for_experiment(
                experiment
            ), f"Participant with field {criterion_name} set to {option} is present in eligible set"


def test_multilingual_criterion(admin_user, sample_participant):
    en = Language.objects.create(name="Engels")
    nl = Language.objects.create(name="Nederlands")

    # multilingual participant
    sample_participant.data.languages.set([en, nl])

    # indifferent
    experiment = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create())
    assert sample_participant in get_eligible_participants_for_experiment(experiment)

    # included
    experiment = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create(multilingual=["Y"]))
    assert sample_participant in get_eligible_participants_for_experiment(experiment)

    # excluded
    experiment = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create(multilingual=["N"]))
    assert sample_participant not in get_eligible_participants_for_experiment(experiment)

    # monolingual participant
    sample_participant.data.languages.set([en])

    # indifferent
    experiment = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create())
    assert sample_participant in get_eligible_participants_for_experiment(experiment)

    # included
    experiment = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create(multilingual=["N"]))
    assert sample_participant in get_eligible_participants_for_experiment(experiment)

    # excluded
    experiment = admin_user.experiments.create(defaultcriteria=DefaultCriteria.objects.create(multilingual=["Y"]))
    assert sample_participant not in get_eligible_participants_for_experiment(experiment)
