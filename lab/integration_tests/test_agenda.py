from datetime import date, datetime, timedelta

import pytest

from agenda.models import Closing


@pytest.fixture
def agenda(sb):
    sb.click('a:contains("Agenda")')


def test_agenda_add_closing(sb, as_admin, agenda):
    sb.click(f'td[data-date="{date.today()}"]')

    start = date.today().strftime('%d-%m-%Y 00:00')
    end = (date.today() + timedelta(days=1)).strftime('%d-%m-%Y 00:00')

    sb.assert_attribute('.closing-start input', 'value', start)
    sb.assert_attribute('.closing-end input', 'value', end)

    sb.click('button:contains("Save")')

    sb.wait_for_element_absent('.action-panel')

    # expect our event to be there after refresh
    sb.refresh()
    sb.assert_element(f'td[data-date="{date.today()}"] .fc-event')
    sb.assert_text('Closed', '.fc-event')
    sb.assert_text('Entire building', '.fc-event')


@pytest.fixture
def sample_closing(db):
    yield Closing.objects.create(
        start=datetime.today(),
        end=datetime.today() + timedelta(days=1),
        is_global=True
    )


def test_agenda_edit_closing(sb, sample_closing, as_admin, agenda):
    sb.click(f'td[data-date="{date.today()}"]')
    sb.assert_element_visible('.action-panel')
    sb.assert_text('Edit closing', '.action-panel')
