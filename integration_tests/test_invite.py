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


def test_cancel_appointment_from_email(apps, participant, mailbox, sb):
    apps.lab.load('admin')  # generate admin user
    Experiment = apps.lab.get_model('experiments', 'Experiment')
    DefaultCriteria = apps.lab.get_model('experiments', 'DefaultCriteria')
    User = apps.lab.get_model('main', 'User')
    experiment = Experiment.objects.create(defaultcriteria=DefaultCriteria.objects.create())

    # somewhat abusing the get_model() calls above to setup django for the following to work
    from experiments.models import make_appointment
    from utils.appointment_mail import send_appointment_mail

    leader = User.objects.first()  # admin
    start = timezone.now()
    end = start + timedelta(hours=1)
    appointment = make_appointment(experiment, participant, leader, start, end)

    send_appointment_mail(appointment)

    mail = mailbox(participant.email)
    assert len(mail) == 1
    html = mail[0].get_payload()[1].get_payload()
    # find (cancellation) link in email
    link = re.search(r'<a href="([^"]+)"', html).group(1)
    sb.open(link)

    # check that the appointment was removed
    with pytest.raises(ObjectDoesNotExist):
        appointment.refresh_from_db()
