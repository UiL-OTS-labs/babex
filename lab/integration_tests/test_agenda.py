from datetime import date, datetime, timedelta

import pytest

from agenda.models import Closing
from experiments.models import Appointment, DefaultCriteria, TimeSlot


@pytest.fixture
def agenda(sb):
    sb.click('a:contains("Agenda")')


def test_agenda_add_closing(sb, as_admin, agenda):
    sb.click(f'td[data-date="{date.today()}"]')

    start = date.today().strftime("%d-%m-%Y 00:00")
    end = (date.today() + timedelta(days=1)).strftime("%d-%m-%Y 00:00")

    sb.assert_attribute(".closing-start input", "value", start)
    sb.assert_attribute(".closing-end input", "value", end)

    sb.click('button:contains("Save")')

    sb.wait_for_element_absent(".action-panel")

    # expect our event to be there after refresh
    sb.refresh()
    sb.assert_element(f'td[data-date="{date.today()}"] .fc-event')
    sb.assert_text("Closed", ".fc-event")
    sb.assert_text("Entire building", ".fc-event")


@pytest.fixture
def sample_closing(db):
    yield Closing.objects.create(start=datetime.today(), end=datetime.today() + timedelta(days=1), is_global=True)


def test_agenda_edit_closing(sb, sample_closing, as_admin, agenda):
    sb.click(f'td[data-date="{date.today()}"]')
    sb.assert_element_visible(".action-panel")
    sb.assert_text("Edit closing", ".action-panel")


@pytest.fixture
def appointment_yesterday(db, sample_experiment, sample_leader, sample_participant):
    midnight = datetime(date.today().year, date.today().month, date.today().day, 0, 0)
    timeslot = TimeSlot.objects.create(
        start=midnight - timedelta(hours=13),
        end=midnight - timedelta(hours=12),
        experiment=sample_experiment,
    )
    yield Appointment.objects.create(
        participant=sample_participant, experiment=sample_experiment, timeslot=timeslot, leader=sample_leader
    )


def test_agenda_set_appointment_outcome(sb, appointment_yesterday, as_leader):
    appointment_yesterday.experiment.leaders.add(as_leader)
    sb.click('a:contains("Agenda")')

    sb.assert_text_visible(appointment_yesterday.participant.name)
    sb.click(f'td[data-date="{appointment_yesterday.start.date()}"]')
    sb.assert_element_visible(".action-panel")
    sb.assert_text("Edit appointment", ".action-panel")

    # appointment is in the past, should not be possible to remove
    sb.assert_element_not_visible("button:contains('Remove')")

    # set outcome
    sb.click("label:contains('No-show')")
    sb.click("Button:contains('Save')")
    sb.assert_element_not_visible(".action-panel")

    # check that outcome is saved after refresh
    sb.reload()
    sb.click(f'td[data-date="{appointment_yesterday.start.date()}"]')
    sb.assert_element_visible('input[value="NOSHOW"]:checked')

    # participant should be available again after a no-show
    sb.click("a:contains(Experiments)")
    sb.click("a:contains(Overview)")
    sb.click("button.icon-menu")
    sb.click("a:contains(Invite)")
    sb.assert_text_visible(appointment_yesterday.participant.name)
