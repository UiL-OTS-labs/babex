import time
from datetime import date, datetime, timedelta

import pytest
from django.core import mail

from experiments.models import Appointment, DefaultCriteria, TimeSlot
from main.models import User


def test_experiment_list(sb, sample_experiment, sample_participant, as_leader):
    as_leader.experiments.add(sample_experiment)
    sb.click("a:contains(Experiments)")
    sb.click("a:contains(Overview)")
    sb.click("button.icon-menu")
    sb.click("a:contains(Invite)")
    sb.assert_text("Baby McBaby")


def test_schedule_appointment(sb, sample_experiment, sample_participant, sample_leader, as_leader):
    sample_experiment.leaders.add(as_leader)
    # test with a differnet leader than the currently logged user
    sample_experiment.leaders.add(sample_leader)

    sb.click("a:contains(Experiments)")
    sb.click("a:contains(Overview)")
    sb.click("button.icon-menu")
    sb.click("a:contains(Invite)")
    sb.click("a.icon-phone")
    sb.click("button:contains(Schedule)")

    # pick time
    tomorrow = date.today() + timedelta(days=1)
    sb.click(f'td[data-date="{tomorrow}"]')
    sb.click('td.fc-timegrid-slot-lane[data-time="10:00:00"]')
    sb.click("button:contains(Next)")

    # pick leader
    sb.select_option_by_text(".modal-content select", "Leader McLeader")

    sb.click("button:contains(Confirm)")
    sb.wait_for_element_not_visible('button:contains("Confirm")')

    # baby mcbaby shouldn't be available anymore
    sb.click("a:contains(Experiments)")
    sb.click("a:contains(Overview)")
    sb.click("button.icon-menu")
    sb.click("a:contains(Invite)")
    sb.assert_text_not_visible("Baby McBaby")

    # check that appointment is visible on agenda
    sb.click("a:contains(Agenda)")
    sb.assert_element(f'td[data-date="{tomorrow}"] .fc-event')

    # appointment should contain both participant and leader names
    sb.assert_text("Baby McBaby", ".fc-event")
    sb.assert_text("Leader McLeader", ".fc-event")

    # check that a confirmation email was sent
    sb.assertEqual(len(mail.outbox), 1)
    sb.assertEqual(mail.outbox[0].to[0], sample_participant.email)

    # check that at least parent name and leader name are in the email contents
    sb.assertIn(sample_participant.parent_name, mail.outbox[0].body)
    sb.assertIn(sample_leader.name, mail.outbox[0].body)
    sb.assertIn(sample_participant.parent_name, mail.outbox[0].alternatives[0][0])
    sb.assertIn(sample_leader.name, mail.outbox[0].alternatives[0][0])


def test_schedule_appointment_edit_email(sb, sample_experiment, sample_participant, sample_leader, as_leader):
    sample_experiment.leaders.add(as_leader)
    sample_experiment.leaders.add(sample_leader)

    sb.click("a:contains(Experiments)")
    sb.click("a:contains(Overview)")
    sb.click("button.icon-menu")
    sb.click("a:contains(Invite)")
    sb.click("a.icon-phone")
    sb.click("button:contains(Schedule)")

    # pick time
    tomorrow = date.today() + timedelta(days=1)
    sb.click(f'td[data-date="{tomorrow}"]')
    sb.click('td.fc-timegrid-slot-lane[data-time="10:00:00"]')
    sb.click("button:contains(Next)")

    # pick leader
    sb.select_option_by_text(".modal-content select", "Leader McLeader")
    # choose to edit mail
    sb.click('label:contains("Edit mail")')
    sb.click("button:contains(Confirm)")

    while not sb.execute_script("return (tinymce.activeEditor && tinymce.activeEditor.getContent())"):
        time.sleep(0.2)

    # set tinymce editor with a custon email string
    test_email = "<em>this is a test email</em>"
    test_email_plain = "this is a test email"
    sb.execute_script('tinymce.activeEditor.setContent("{}")'.format(test_email))

    sb.assertEqual(len(mail.outbox), 0)
    sb.click("button:contains(Confirm)")
    sb.wait_for_element_not_visible('button:contains("Confirm")')

    # check the email was sent
    sb.assertEqual(len(mail.outbox), 1)
    sb.assertEqual(mail.outbox[0].to[0], sample_participant.email)
    sb.assertIn(test_email_plain, mail.outbox[0].body)
    sb.assertIn(test_email, mail.outbox[0].alternatives[0][0])


def test_call_exclusion(sb, sample_experiment, sample_participant, sample_leader, as_admin):
    sample_experiment.leaders.add(sample_leader)

    sb.click("a:contains(Experiments)")
    sb.click("a:contains(Overview)")
    sb.click("button.icon-menu")
    sb.click("a:contains(Invite)")
    sb.click("a.icon-phone")

    # indicates participant can't participate
    sb.click('input[value="EXCLUDE"]')
    sb.click("button:contains(Save)")

    # baby mcbaby shouldn't be available anymore
    sb.click("a:contains(Experiments)")
    sb.click("a:contains(Overview)")
    sb.click("button.icon-menu")
    sb.click("a:contains(Invite)")
    sb.assert_text_not_visible("Baby McBaby")


def test_reschedule_participant(sb, sample_experiment, sample_participant, sample_leader, as_leader):
    """it should be possible to make a new appointment with the same participant, if a previous appointment was canceled"""

    sample_experiment.leaders.add(as_leader)

    # create a test appointment
    timeslot = TimeSlot.objects.create(
        start=datetime.now() + timedelta(hours=24),
        end=datetime.now() + timedelta(hours=25),
        experiment=sample_experiment,
        max_places=1,
    )
    appointment = Appointment.objects.create(
        participant=sample_participant, experiment=sample_experiment, timeslot=timeslot, leader=sample_leader
    )

    # baby mcbaby shouldn't be available anymore
    sb.click("a:contains(Experiments)")
    sb.click("a:contains(Overview)")
    sb.click("button.icon-menu")
    sb.click("a:contains(Invite)")
    sb.assert_text_not_visible("Baby McBaby")

    appointment.cancel()

    # baby mcbaby should be available again
    sb.click("a:contains(Experiments)")
    sb.click("a:contains(Overview)")
    sb.click("button.icon-menu")
    sb.click("a:contains(Invite)")
    sb.assert_text_visible("Baby McBaby")
