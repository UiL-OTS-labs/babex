import time
from datetime import date, datetime, timedelta

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from playwright.sync_api import expect

from experiments.models import Appointment, TimeSlot


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
    while not page.evaluate("() => (tinymce.activeEditor && tinymce.activeEditor.getContent())"):
        time.sleep(0.2)
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

    while not page.evaluate("() => (tinymce.activeEditor && tinymce.activeEditor.getContent())"):
        time.sleep(0.2)

    # set tinymce editor with a custom email string
    test_email = "<em>this is a test email</em>"
    test_email_plain = "this is a test email"
    page.evaluate('() => tinymce.activeEditor.setContent("{}")'.format(test_email))

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
