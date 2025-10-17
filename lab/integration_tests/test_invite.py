import time
from datetime import date, datetime, timedelta

import pytest
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from playwright.sync_api import expect

from experiments.models import Appointment, TimeSlot
from participants.models import Language, Participant


def test_experiment_list(page, sample_experiment, sample_participant, as_leader):
    as_leader.experiments.add(sample_experiment)
    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()
    expect(page.get_by_text("Baby McBaby")).to_be_visible()


def test_schedule_appointment(page, sample_experiment, sample_participant, sample_leader, as_leader):
    sample_experiment.leaders.add(as_leader)
    # test with a differnet leader than the currently logged user
    sample_experiment.leaders.add(sample_leader)

    # add an email attachment to the experiment
    test_file_content = "this is a test file"
    sample_experiment.attachments.create(
        filename="test-file", file=SimpleUploadedFile("test.txt", test_file_content.encode())
    )

    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()
    page.locator("td.actions").get_by_text("Call").click()
    page.locator("button").get_by_text("Schedule").click()

    # pick time
    tomorrow = date.today() + timedelta(days=1)
    page.click(f'td[data-date="{tomorrow}"]')
    page.click('td.fc-timegrid-slot-lane[data-time="10:00:00"]')
    page.locator("button").get_by_text("Next").click()

    # pick leader
    page.locator(".modal-content select").select_option("Leader McLeader")

    page.locator("button").get_by_text("Confirm").click()
    page.get_by_role("button", name="Confirm").wait_for(state="hidden")

    # wait for email content to be ready
    expect(page.frame_locator("#mce_0_ifr").locator("body")).to_be_visible()

    page.locator("button").get_by_text("Send").click()
    page.get_by_role("button", name="Send").wait_for(state="hidden")

    # baby mcbaby shouldn't be available anymore
    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()
    expect(page.get_by_text("Baby McBaby")).not_to_be_visible()

    # check that appointment is visible on agenda
    page.locator("a").get_by_text("Agenda").click()
    expect(page.locator(f'td[data-date="{tomorrow}"] .fc-event')).to_be_visible()

    # appointment should contain both participant and leader names
    expect(page.locator(".fc-event").get_by_text("Baby McBaby")).to_be_visible()
    expect(page.locator(".fc-event").get_by_text("Leader McLeader")).to_be_visible()

    # check that a confirmation email was sent
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to[0] == sample_participant.email

    # check that the attachment is present
    assert mail.outbox[0].attachments[0] == ("test-file", test_file_content, "text/plain")

    # check that at least parent name and leader name are in the email contents
    assert sample_participant.parent_last_name in mail.outbox[0].body
    assert sample_leader.name in mail.outbox[0].body
    assert sample_participant.parent_last_name in mail.outbox[0].alternatives[0][0]
    assert sample_leader.name in mail.outbox[0].alternatives[0][0]


def test_schedule_appointment_edit_email(page, sample_experiment, sample_participant, sample_leader, as_leader):
    sample_experiment.leaders.add(as_leader)
    sample_experiment.leaders.add(sample_leader)

    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()
    page.locator("td.actions").get_by_text("Call").click()
    page.locator("button").get_by_text("Schedule").click()

    # pick time
    tomorrow = date.today() + timedelta(days=1)
    page.click(f'td[data-date="{tomorrow}"]')
    page.click('td.fc-timegrid-slot-lane[data-time="10:00:00"]')
    page.locator("button").get_by_text("Next").click()

    # pick leader
    page.locator(".modal-content select").select_option("Leader McLeader")
    page.locator("button").get_by_text("Confirm").click()

    # set tinymce editor with a custom email string
    test_email = "this is a test email"
    test_email_plain = "this is a test email"
    expect(page.frame_locator("#mce_0_ifr").locator("body div")).not_to_have_count(0)
    page.frame_locator("#mce_0_ifr").locator("body").fill(test_email)
    page.keyboard.press("Control+A")
    page.keyboard.press("Control+I")

    assert len(mail.outbox) == 0
    page.locator("button").get_by_text("Send").click()
    page.get_by_role("button", name="Send").wait_for(state="hidden")

    # check the email was sent
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to[0] == sample_participant.email
    assert test_email_plain in mail.outbox[0].body
    assert test_email in mail.outbox[0].alternatives[0][0]


def test_call_exclusion(page, sample_experiment, sample_participant, sample_leader, as_admin):
    sample_experiment.leaders.add(sample_leader)

    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()
    page.locator("td.actions").get_by_text("Call").click()

    # indicates participant can't participate
    page.click('input[value="EXCLUDE"]')
    page.locator("button").get_by_text("Save").click()
    page.locator("button").get_by_text("Save").wait_for(state="hidden")

    # baby mcbaby shouldn't be available anymore
    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()
    expect(page.get_by_text("Baby McBaby")).not_to_be_visible()


def test_reschedule_participant(page, sample_experiment, sample_participant, sample_leader, as_leader):
    """it should be possible to make a new appointment with the same participant, if a previous appointment was canceled"""

    sample_experiment.leaders.add(sample_leader)
    sample_experiment.leaders.add(as_leader)

    # create a test appointment
    timeslot = TimeSlot.objects.create(
        start=datetime.now() + timedelta(hours=24),
        end=datetime.now() + timedelta(hours=25),
        experiment=sample_experiment,
    )
    appointment = Appointment.objects.create(
        participant=sample_participant, experiment=sample_experiment, timeslot=timeslot, leader=sample_leader
    )

    # baby mcbaby shouldn't be available anymore
    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()
    expect(page.get_by_text("Baby McBaby")).not_to_be_visible()

    appointment.cancel()

    # baby mcbaby should be available again
    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()
    expect(page.get_by_text("Baby McBaby")).to_be_visible()


def test_call_deactivate(page, sample_experiment, sample_participant, sample_leader, as_admin):
    sample_experiment.leaders.add(sample_leader)

    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()
    page.locator("td.actions").get_by_text("Call").click()

    page.click('input[value="DEACTIVATE"]')
    btn = page.locator("button").get_by_text("Save")
    btn.click()
    btn.wait_for(state="hidden")

    # check that confirmation mail was sent to parent
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to[0] == sample_participant.email


def test_call_status_after_cancellation(page, sample_experiment, sample_participant, sample_leader, as_leader):
    """a participant should not show up as confirmed on the call list after an appointment has been cancelled"""

    sample_experiment.leaders.add(sample_leader)
    sample_experiment.leaders.add(as_leader)

    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()
    page.locator("td.actions").get_by_text("Call").click()
    page.locator("button").get_by_text("Schedule").click()

    # pick time
    tomorrow = date.today() + timedelta(days=1)
    page.click(f'td[data-date="{tomorrow}"]')
    page.click('td.fc-timegrid-slot-lane[data-time="10:00:00"]')
    page.locator("button").get_by_text("Next").click()

    # pick leader
    page.locator(".modal-content select").select_option("Leader McLeader")
    page.locator("button").get_by_text("Confirm").click()

    expect(page.frame_locator("#mce_0_ifr").locator("body")).to_be_visible()

    page.locator("button").get_by_text("Send").click()
    page.get_by_role("button", name="Send").wait_for(state="hidden")

    Appointment.objects.last().cancel()

    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()
    expect(page.get_by_text("Baby McBaby")).to_be_visible()
    expect(page.get_by_text("Confirmed")).not_to_be_visible()


@pytest.mark.freeze_time("2021-01-01")
def test_sort_participants_by_age(page, sample_experiment, as_leader):
    as_leader.experiments.add(sample_experiment)
    pp1 = Participant.objects.create(
        email="baby@baby.com",
        name="Baby1",
        sex=Participant.Sex.UNKNOWN,
        parent_first_name="Parent",
        parent_last_name="McParent",
        birth_date=date(2020, 1, 1),
        phonenumber="987654321",
        dyslexic_parent=Participant.WhichParent.NEITHER,
        email_subscription=True,
    )
    pp2 = Participant.objects.create(
        email="baby3@baby.com",
        name="Baby2",
        sex=Participant.Sex.UNKNOWN,
        parent_first_name="Parent",
        parent_last_name="McParent",
        birth_date=date(2019, 1, 1),
        phonenumber="987654321",
        dyslexic_parent=Participant.WhichParent.NEITHER,
        email_subscription=True,
    )
    pp3 = Participant.objects.create(
        email="baby2@baby.com",
        name="Baby3",
        sex=Participant.Sex.UNKNOWN,
        parent_first_name="Parent",
        parent_last_name="McParent",
        birth_date=date(2010, 1, 1),
        phonenumber="987654321",
        dyslexic_parent=Participant.WhichParent.NEITHER,
        email_subscription=True,
    )

    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()

    time.sleep(1)
    page.locator("#DataTables_Table_0 th").nth(1).click()

    rows = page.locator("#DataTables_Table_0 tbody tr")
    rendered_order = [rows.nth(i).locator("td").nth(0).inner_text() for i in range(rows.count())]

    assert len(rendered_order) == 3
    assert rendered_order == [pp3.name, pp2.name, pp1.name]


def test_sort_participants_by_date_of_birth(page, sample_experiment, as_leader):
    as_leader.experiments.add(sample_experiment)
    pp1 = Participant.objects.create(
        email="baby@baby.com",
        name="Baby1",
        sex=Participant.Sex.UNKNOWN,
        parent_first_name="Parent",
        parent_last_name="McParent",
        birth_date=date(2020, 1, 1),
        phonenumber="987654321",
        dyslexic_parent=Participant.WhichParent.NEITHER,
        email_subscription=True,
    )
    pp2 = Participant.objects.create(
        email="baby3@baby.com",
        name="Baby2",
        sex=Participant.Sex.UNKNOWN,
        parent_first_name="Parent",
        parent_last_name="McParent",
        birth_date=date(2020, 2, 1),
        phonenumber="987654321",
        dyslexic_parent=Participant.WhichParent.NEITHER,
        email_subscription=True,
    )
    pp3 = Participant.objects.create(
        email="baby2@baby.com",
        name="Baby3",
        sex=Participant.Sex.UNKNOWN,
        parent_first_name="Parent",
        parent_last_name="McParent",
        birth_date=date(2020, 10, 1),
        phonenumber="987654321",
        dyslexic_parent=Participant.WhichParent.NEITHER,
        email_subscription=True,
    )

    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()

    time.sleep(1)
    page.locator("#DataTables_Table_0 th").nth(2).click()
    # click twice to order descending
    page.locator("#DataTables_Table_0 th").nth(2).click()

    rows = page.locator("#DataTables_Table_0 tbody tr")
    rendered_order = [rows.nth(i).locator("td").nth(0).inner_text() for i in range(rows.count())]

    assert len(rendered_order) == 3
    assert rendered_order == [pp3.name, pp2.name, pp1.name]
