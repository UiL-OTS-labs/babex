import random
import re
import string
from datetime import date, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone


import pytest


@pytest.fixture
def participant(apps):
    suffix = ''.join(random.choice(string.digits) for i in range(4))
    Participant = apps.lab.get_model("participants", "Participant")
    participant = Participant.objects.create(
        email=f"baby{suffix}@baby.com",
        name="Baby McBaby",
        parent_name="Parent McParent",
        birth_date=date(2020, 1, 1),
        multilingual=False,
        phonenumber="987654321",
        dyslexic_parent=False,
        language="nl",
        capable=True,
        email_subscription=True,
    )
    yield participant
    participant.delete()


def test_cancel_appointment_from_email(apps, participant, mailbox, link_from_mail, sb):
    apps.lab.load('admin')  # generate admin user
    Experiment = apps.lab.get_model('experiments', 'Experiment')
    DefaultCriteria = apps.lab.get_model('experiments', 'DefaultCriteria')
    User = apps.lab.get_model('main', 'User')
    Appointment = apps.lab.get_model('experiments', 'Appointment')
    experiment = Experiment.objects.create(defaultcriteria=DefaultCriteria.objects.create())

    # somewhat abusing the get_model() calls above to setup django for the following to work
    from experiments.models import make_appointment
    from utils.appointment_mail import send_appointment_mail

    leader = User.objects.first()  # admin
    start = timezone.now()
    end = start + timedelta(hours=1)
    experiment.leaders.add(leader)
    experiment.save()
    appointment = make_appointment(experiment, participant, leader, start, end)

    send_appointment_mail(appointment)

    sb.open(link_from_mail(participant.email))

    # check that the appointment was canceled
    appointment.refresh_from_db()
    assert appointment.outcome == Appointment.Outcome.CANCELED

    # check that leader was notified
    mail = mailbox(leader.email)
    assert len(mail) == 1
    text = mail[0].get_payload()[0].get_payload()
    assert participant.name in text
    assert 'unsubscribed' in text

    # delete appointment so that the participant can be deleted as well
    appointment.delete()


def test_appointment_in_parent_overview(apps, participant, mailbox, sb, login_as):
    apps.lab.load('admin')  # generate admin user
    Experiment = apps.lab.get_model('experiments', 'Experiment')
    DefaultCriteria = apps.lab.get_model('experiments', 'DefaultCriteria')
    User = apps.lab.get_model('main', 'User')
    Appointment = apps.lab.get_model('experiments', 'Appointment')
    experiment = Experiment.objects.create(defaultcriteria=DefaultCriteria.objects.create())

    # somewhat abusing the get_model() calls above to setup django for the following to work
    from experiments.models import make_appointment
    from utils.appointment_mail import send_appointment_mail

    leader = User.objects.first()  # admin
    start = timezone.now()
    end = start + timedelta(hours=1)
    experiment.leaders.add(leader)
    experiment.save()
    appointment = make_appointment(experiment, participant, leader, start, end)

    login_as(participant.email)
    sb.assert_text_visible('Appointments')
    sb.assert_text_visible(experiment.name)
    sb.assert_text_visible(leader.name)

    # delete appointment so that the participant can be deleted as well
    appointment.delete()
