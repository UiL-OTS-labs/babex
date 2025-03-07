import random
import string
from datetime import date, timedelta
from django.utils import timezone


import pytest

from playwright.sync_api import expect


@pytest.fixture
def participant(apps):
    suffix = ''.join(random.choice(string.digits) for i in range(4))
    Participant = apps.lab.get_model("participants", "Participant")
    participant = Participant.objects.create(
        email=f"baby{suffix}@baby.com",
        name="Baby McBaby",
        parent_first_name="Parent",
        parent_last_name="McParent",
        birth_date=date(2020, 1, 1),
        phonenumber="987654321",
        dyslexic_parent=Participant.WhichParent.UNKNOWN,
        email_subscription=True,
    )
    yield participant
    participant.delete()


def test_cancel_appointment_from_email(apps, participant, mailbox, link_from_mail, page):
    apps.lab.load('admin')  # generate admin user
    Experiment = apps.lab.get_model('experiments', 'Experiment')
    User = apps.lab.get_model('main', 'User')
    Appointment = apps.lab.get_model('experiments', 'Appointment')
    experiment = Experiment.objects.create(duration=10, session_duration=20)

    # somewhat abusing the get_model() calls above to setup django for the following to work
    from experiments.models import make_appointment
    from utils.appointment_mail import send_appointment_mail, prepare_appointment_mail

    leader = User.objects.first()  # admin
    start = timezone.now()
    experiment.leaders.add(leader)
    experiment.save()
    appointment = make_appointment(experiment, participant, leader, start)

    send_appointment_mail(appointment, prepare_appointment_mail(appointment))

    page.goto(link_from_mail(participant.email))

    # check that the appointment was canceled
    appointment.refresh_from_db()
    assert appointment.outcome == Appointment.Outcome.CANCELED

    # check that leader was notified
    try:
        mail = mailbox(leader.email)
        assert len(mail) == 1
        text = mail[0].get_payload()[0].get_payload()
        assert participant.name not in text  # avoid exposing participant name in email
        assert 'canceled' in text
    finally:
        # delete appointment so that the participant can be deleted as well
        appointment.delete()


def test_appointment_in_parent_overview(apps, participant, mailbox, page, login_as):
    apps.lab.load('admin')  # generate admin user
    Experiment = apps.lab.get_model('experiments', 'Experiment')
    User = apps.lab.get_model('main', 'User')
    experiment = Experiment.objects.create(duration=10,
                                           session_duration=20,
                                           name='Test Experiment')

    # somewhat abusing the get_model() calls above to setup django for the following to work
    from experiments.models import make_appointment

    leader = User.objects.first()  # admin
    start = timezone.now()
    experiment.leaders.add(leader)
    experiment.save()
    appointment = make_appointment(experiment, participant, leader, start)

    login_as(participant.email)
    try:
        expect(page.get_by_text('Appointments')).to_be_visible()
        expect(page.get_by_text(experiment.name)).to_be_visible()
        expect(page.get_by_text(leader.name)).to_be_visible()
    finally:
        # delete appointment so that the participant can be deleted as well
        appointment.delete()


def test_past_appointment_not_in_parent_overview(apps, participant, mailbox, page, login_as):
    apps.lab.load('admin')  # generate admin user
    Experiment = apps.lab.get_model('experiments', 'Experiment')
    User = apps.lab.get_model('main', 'User')
    experiment = Experiment.objects.create(duration=10,
                                           session_duration=20,
                                           name='Test Experiment')

    # somewhat abusing the get_model() calls above to setup django for the following to work
    from experiments.models import make_appointment

    leader = User.objects.first()  # admin
    start = timezone.now() - timedelta(days=30)
    experiment.leaders.add(leader)
    experiment.save()
    appointment = make_appointment(experiment, participant, leader, start)

    login_as(participant.email)
    try:
        expect(page.get_by_text('Appointments')).to_be_visible()
        expect(page.get_by_text(experiment.name)).not_to_be_visible()
        expect(page.get_by_text(leader.name)).not_to_be_visible()
    finally:
        # delete appointment so that the participant can be deleted as well
        appointment.delete()
