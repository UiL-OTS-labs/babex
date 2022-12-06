from datetime import date
import pytest

from main.models import User
from experiments.models import Experiment, DefaultCriteria
from leaders.models import Leader
from participants.models import Participant


@pytest.fixture
def sample_experiment(admin_user, db):
    yield admin_user.leader.experiments.create(
        defaultcriteria=DefaultCriteria.objects.create()
    )


@pytest.fixture
def sample_participant(db):
    yield Participant.objects.create(
        email='baby@baby.com',
        name='Baby McBaby',
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
    user = User.objects.create(username='leader')
    yield Leader.objects.create(name='Leader McLeader',
                                phonenumber='23456789',
                                user=user)


def test_experiment_list(sb, sample_experiment, sample_participant, as_admin):
    sb.click('a:contains(Experiments)')
    sb.click('a:contains(Overview)')
    sb.click('a:contains(Invite)')
    sb.assert_text('Baby McBaby')


def test_schedule_appointment(sb, sample_experiment, sample_participant, sample_leader, as_admin):
    sample_experiment.additional_leaders.add(sample_leader)

    sb.click('a:contains(Experiments)')
    sb.click('a:contains(Overview)')
    sb.click('a:contains(Invite)')
    sb.click('a.icon-phone')
    sb.click('button:contains(Schedule)')

    # pick time
    sb.click(f'td[data-date="{date.today()}"]')
    sb.click('td.fc-timegrid-slot-lane[data-time="10:00:00"]')
    sb.click('button:contains(Next)')

    # pick leader
    sb.select_option_by_text('.modal-content select', 'Leader McLeader')

    sb.click('button:contains(Confirm)')
    sb.wait_for_element_not_visible('button:contains("Confirm")')

    # baby mcbaby shouldn't be available anymore
    sb.click('a:contains(Experiments)')
    sb.click('a:contains(Overview)')
    sb.click('a:contains(Invite)')
    sb.assert_text_not_visible('Baby McBaby')

    # check that appointment is visible on agenda
    sb.click('a:contains(Agenda)')
    sb.assert_element(f'td[data-date="{date.today()}"] .fc-event')

    # appointment should contain both participant and leader names
    sb.assert_text('Baby McBaby', '.fc-event')
    sb.assert_text('Leader McLeader', '.fc-event')
