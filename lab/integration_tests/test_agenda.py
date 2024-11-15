import time
from datetime import date, datetime, timedelta

import pytest
from django.core import mail
from django.utils import timezone
from playwright.sync_api import expect

from agenda.models import Closing
from experiments.models import Appointment, TimeSlot


@pytest.fixture
def agenda(page):
    page.locator("a").get_by_text("Agenda").click()


def test_agenda_add_closing(page, as_admin, agenda):
    page.click(f'td[data-date="{date.today()}"]')

    start = date.today().strftime("%d-%m-%Y 00:00")
    end = (date.today() + timedelta(days=1)).strftime("%d-%m-%Y 00:00")

    expect(page.locator(".closing-start input")).to_have_value(start)
    expect(page.locator(".closing-end input")).to_have_value(end)

    page.locator("button").get_by_text("Save").click()

    expect(page.locator(".action-panel")).not_to_be_visible()

    # expect our event to be there after refresh
    page.reload()
    expect(page.locator(f'td[data-date="{date.today()}"] .fc-event')).to_be_attached()
    expect(page.locator(".fc-event")).to_contain_text("Closed")
    expect(page.locator(".fc-event")).to_contain_text("Entire building")


@pytest.fixture
def sample_closing(db):
    yield Closing.objects.create(start=datetime.today(), end=datetime.today() + timedelta(days=1), is_global=True)


def test_agenda_edit_closing(page, sample_closing, as_admin, agenda):
    page.click(f'td[data-date="{date.today()}"]')
    expect(page.locator(".action-panel")).to_be_visible()
    expect(page.locator(".action-panel")).to_contain_text("Edit closing")


@pytest.fixture
def appointment_yesterday(db, sample_experiment, sample_leader, sample_participant):
    sample_experiment.leaders.add(sample_leader)
    midnight = datetime(
        date.today().year, date.today().month, date.today().day, 0, 0, tzinfo=timezone.get_current_timezone()
    )
    timeslot = TimeSlot.objects.create(
        start=midnight - timedelta(hours=13),
        end=midnight - timedelta(hours=12),
        experiment=sample_experiment,
    )
    yield Appointment.objects.create(
        participant=sample_participant, experiment=sample_experiment, timeslot=timeslot, leader=sample_leader
    )


@pytest.fixture
def appointment_tomorrow(db, sample_experiment, sample_leader, sample_participant):
    sample_experiment.leaders.add(sample_leader)
    start = datetime(
        date.today().year, date.today().month, date.today().day, 12, 0, tzinfo=timezone.get_current_timezone()
    ) + timedelta(days=1)
    timeslot = TimeSlot.objects.create(
        start=start,
        end=start + timedelta(hours=1),
        experiment=sample_experiment,
    )
    yield Appointment.objects.create(
        participant=sample_participant, experiment=sample_experiment, timeslot=timeslot, leader=sample_leader
    )


def test_agenda_set_appointment_outcome(page, appointment_yesterday, as_leader):
    appointment_yesterday.experiment.leaders.add(as_leader)
    page.locator("a").get_by_text("Agenda").click()

    expect(page.get_by_text(appointment_yesterday.participant.name)).to_be_visible()
    page.click(f'td[data-date="{appointment_yesterday.start.date()}"]')
    expect(page.locator(".action-panel")).to_be_visible()
    expect(page.locator(".action-panel")).to_contain_text("Edit appointment")

    # appointment is in the past, should not be possible to remove
    expect(page.locator("button").get_by_text("Remove")).not_to_be_visible()

    # set outcome
    page.locator("label").get_by_text("No-show").click()
    page.locator("Button").get_by_text("Save").click()
    expect(page.locator(".action-panel")).not_to_be_visible()

    # check that outcome is saved after refresh
    page.reload()
    page.click(f'td[data-date="{appointment_yesterday.start.date()}"]')
    expect(page.locator('input[value="NOSHOW"]:checked')).to_be_visible()

    # participant should be available again after a no-show
    page.get_by_role("button", name="Experiments").click()
    page.get_by_role("link", name="Overview").click()
    page.click("button.icon-menu")
    page.locator("a").get_by_text("Invite").click()
    expect(page.get_by_text(appointment_yesterday.participant.name)).to_be_visible()


def test_agenda_modify_appointment(page, appointment_tomorrow, as_leader):
    appointment_tomorrow.experiment.leaders.add(as_leader)
    page.locator("a").get_by_text("Agenda").click()

    page.click(f'td[data-date="{appointment_tomorrow.start.date()}"]')
    original_time = appointment_tomorrow.timeslot.start
    new_time = original_time + timedelta(days=3)

    page.fill(".appointment-start input", new_time.strftime("%d-%m-%Y %H:%M"))
    page.click(".action-panel .save")

    page.locator(".action-panel .save").wait_for(state="hidden")
    appointment_tomorrow.refresh_from_db()
    assert appointment_tomorrow.timeslot.start == new_time

    # FIXME
    time.sleep(1)

    # check that an appointment update email was sent
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to[0] == appointment_tomorrow.participant.email
