from datetime import date, datetime, timedelta
import time
import pytest
from django.core import mail

from main.models import User
from experiments.models import Appointment, DefaultCriteria, TimeSlot
from participants.models import Participant


@pytest.fixture
def sample_experiment(admin_user, db):
    yield admin_user.experiments.create(
        defaultcriteria=DefaultCriteria.objects.create()
    )


@pytest.fixture
def sample_participant(db):
    yield Participant.objects.create(
        email='baby@baby.com',
        name='Baby McBaby',
        parent_name='Parent McParent',
        birth_date=date(2020, 1, 1),
        multilingual=False,
        phonenumber='987654321',
        dyslexic_parent=False,
        language='nl',
        capable=True,
        email_subscription=True
    )


@pytest.fixture
def sample_leader(db):
    yield User.objects.create(name='Leader McLeader',
                              username='leader',
                              phonenumber='23456789')


@pytest.fixture
def sample_appointment(sample_experiment, sample_participant, sample_leader, db):
    timeslot = TimeSlot.objects.create(
        start=datetime(2023, 1, 1, 9, 0),
        end=datetime(2023, 1, 1, 10, 0),
        experiment=sample_experiment,
        max_places=1
    )
    yield Appointment.objects.create(
        participant=sample_participant,
        experiment=sample_experiment,
        timeslot=timeslot,
        leader=sample_leader)


def test_experiment_list(sb, sample_experiment, sample_participant, as_admin):
    sb.click('a:contains(Experiments)')
    sb.click('a:contains(Overview)')
    sb.click('button.icon-menu')
    sb.click('a:contains(Invite)')
    sb.assert_text('Baby McBaby')


def test_schedule_appointment(sb, sample_experiment, sample_participant, sample_leader, as_admin):
    sample_experiment.leaders.add(sample_leader)

    sb.click('a:contains(Experiments)')
    sb.click('a:contains(Overview)')
    sb.click('button.icon-menu')
    sb.click('a:contains(Invite)')
    sb.click('a.icon-phone')
    sb.click('button:contains(Schedule)')

    # pick time
    tomorrow = date.today() + timedelta(days=1)
    sb.click(f'td[data-date="{tomorrow}"]')
    sb.click('td.fc-timegrid-slot-lane[data-time="10:00:00"]')
    sb.click('button:contains(Next)')

    # pick leader
    sb.select_option_by_text('.modal-content select', 'Leader McLeader')

    sb.click('button:contains(Confirm)')
    sb.wait_for_element_not_visible('button:contains("Confirm")')

    # baby mcbaby shouldn't be available anymore
    sb.click('a:contains(Experiments)')
    sb.click('a:contains(Overview)')
    sb.click('button.icon-menu')
    sb.click('a:contains(Invite)')
    sb.assert_text_not_visible('Baby McBaby')

    # check that appointment is visible on agenda
    sb.click('a:contains(Agenda)')
    sb.assert_element(f'td[data-date="{tomorrow}"] .fc-event')

    # appointment should contain both participant and leader names
    sb.assert_text('Baby McBaby', '.fc-event')
    sb.assert_text('Leader McLeader', '.fc-event')

    # check that a confirmation email was sent
    sb.assertEqual(len(mail.outbox), 1)
    sb.assertEqual(mail.outbox[0].to[0], sample_participant.email)

    # check that at least parent name and leader name are in the email contents
    sb.assertIn(sample_participant.parent_name, mail.outbox[0].body)
    sb.assertIn(sample_leader.name, mail.outbox[0].body)
    sb.assertIn(sample_participant.parent_name, mail.outbox[0].alternatives[0][0])
    sb.assertIn(sample_leader.name, mail.outbox[0].alternatives[0][0])


def test_schedule_appointment_edit_email(sb, sample_experiment, sample_participant, sample_leader, as_admin):
    sample_experiment.leaders.add(sample_leader)

    sb.click('a:contains(Experiments)')
    sb.click('a:contains(Overview)')
    sb.click('button.icon-menu')
    sb.click('a:contains(Invite)')
    sb.click('a.icon-phone')
    sb.click('button:contains(Schedule)')

    # pick time
    tomorrow = date.today() + timedelta(days=1)
    sb.click(f'td[data-date="{tomorrow}"]')
    sb.click('td.fc-timegrid-slot-lane[data-time="10:00:00"]')
    sb.click('button:contains(Next)')

    # pick leader
    sb.select_option_by_text('.modal-content select', 'Leader McLeader')
    # choose to edit mail
    sb.click('label:contains("Edit mail")')
    sb.click('button:contains(Confirm)')

    while not sb.execute_script('return tinymce.activeEditor.getContent()'):
        time.sleep(0.2)

    # set tinymce editor with a custon email string
    test_email = '<em>this is a test email</em>'
    test_email_plain = 'this is a test email'
    sb.execute_script('tinymce.activeEditor.setContent("{}")'.format(test_email))

    sb.assertEqual(len(mail.outbox), 0)
    sb.click('button:contains(Confirm)')
    sb.wait_for_element_not_visible('button:contains("Confirm")')

    # check the email was sent
    sb.assertEqual(len(mail.outbox), 1)
    sb.assertEqual(mail.outbox[0].to[0], sample_participant.email)
    sb.assertIn(test_email_plain, mail.outbox[0].body)
    sb.assertIn(test_email, mail.outbox[0].alternatives[0][0])
