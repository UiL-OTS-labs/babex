from datetime import date, timedelta

import pytest
from base import as_admin


@pytest.fixture
def agenda(sb):
    sb.click('a:contains("Agenda")')


def test_agenda_add_closing(sb, as_admin, agenda):
    today_aria = date.today().strftime('%B %d, %Y')
    sb.click(f'a[aria-label="{today_aria}"]')

    start = date.today().strftime('%Y-%m-%d 00:00')
    end = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d 00:00')

    sb.assert_attribute('#id_start', 'value', start)
    sb.assert_attribute('#id_end', 'value', end)
