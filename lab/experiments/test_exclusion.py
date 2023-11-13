from datetime import datetime, timedelta

from experiments.models import DefaultCriteria, TimeSlot
from experiments.utils.exclusion import get_eligible_participants_for_experiment
from participants.models import Participant


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


def test_dyslexia_required(admin_user, sample_participant):
    experiment = admin_user.experiments.create(
        defaultcriteria=DefaultCriteria.objects.create(dyslexia=DefaultCriteria.Dyslexia.YES)
    )
    for value in [Participant.WhichParent.FEMALE, Participant.WhichParent.MALE, Participant.WhichParent.BOTH]:
        sample_participant.dyslexic_parent = value
        sample_participant.save()
        assert sample_participant in get_eligible_participants_for_experiment(experiment)
    for value in [Participant.WhichParent.NEITHER, Participant.WhichParent.UNKNOWN]:
        sample_participant.dyslexic_parent = value
        sample_participant.save()
        assert sample_participant not in get_eligible_participants_for_experiment(experiment)


def test_dyslexia_excluded(admin_user, sample_participant):
    experiment = admin_user.experiments.create(
        defaultcriteria=DefaultCriteria.objects.create(dyslexia=DefaultCriteria.Dyslexia.NO)
    )
    for value in [
        Participant.WhichParent.FEMALE,
        Participant.WhichParent.MALE,
        Participant.WhichParent.BOTH,
        Participant.WhichParent.UNKNOWN,
    ]:
        sample_participant.dyslexic_parent = value
        sample_participant.save()
        assert sample_participant not in get_eligible_participants_for_experiment(experiment)
    for value in [Participant.WhichParent.NEITHER]:
        sample_participant.dyslexic_parent = value
        sample_participant.save()
        assert sample_participant in get_eligible_participants_for_experiment(experiment)


def test_dyslexia_indifferent(admin_user, sample_participant):
    experiment = admin_user.experiments.create(
        defaultcriteria=DefaultCriteria.objects.create(dyslexia=DefaultCriteria.Dyslexia.INDIFFERENT)
    )
    for value in [choice[0] for choice in Participant.WhichParent.choices]:
        sample_participant.dyslexic_parent = value
        sample_participant.save()
        assert sample_participant in get_eligible_participants_for_experiment(experiment)
