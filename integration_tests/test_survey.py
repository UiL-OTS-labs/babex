import re
import random
import string
import time
from datetime import date

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


@pytest.fixture(scope='module')
def survey(apps):
    SurveyDefinition = apps.lab.get_model("survey_admin", "SurveyDefinition")
    survey_def = {
        "pages": [
            {"intro": "first page", "questions": [{"template": "yesno", "prompt": "this is a test question"}]},
            {"intro": "second page", "questions": [{"template": "yesno", "prompt": "this is another test question"}]}
        ]
    }
    sd = SurveyDefinition.objects.create(name="Test Survey", content=survey_def)
    yield sd
    sd.surveyinvite_set.all().delete()
    sd.delete()


def test_survey_invite(sb, apps, as_admin, participant, survey, mailbox):
    # send survey invite as admin
    sb.switch_to_driver(as_admin)
    sb.click("a:contains(Surveys)")
    sb.click("button.dropdown-toggle")
    sb.click("a:contains(invite)")
    sb.click('input[type="checkbox"]')
    sb.click("button:contains(send)")

    # read survey invite mail
    mail = mailbox(participant.email)
    assert len(mail)
    html = mail[0].get_payload()[1].get_payload()
    # find link in email
    # it should authenticate us an redirect directly to the survey
    link = re.search(r'<a href="([^"]+)"', html).group(1)
    sb.open(link)

    # check that at least the question text is visible
    sb.assert_text_visible("this is a test question")


@pytest.fixture
def survey_invite(participant, survey):
    invite = survey.surveyinvite_set.create(survey=survey, participant=participant)
    return invite


@pytest.fixture
def parent_open_survey(sb, apps, participant, survey_invite):
    def delegate():
        # try to login via email
        sb.switch_to_default_driver()
        sb.open(survey_invite.get_link())
        return sb
    yield delegate
    survey_invite.delete()


def test_survey_pages(parent_open_survey):
    as_parent = parent_open_survey()

    # check that the first page is visible
    as_parent.assert_text_visible("first page")

    # check that you can continue to the next page
    as_parent.click('button:contains(Continue)')
    as_parent.assert_text_visible("second page")

    # and go back to the first page
    as_parent.click('button:contains(Back)')
    as_parent.assert_text_visible("first page")

    # check that responses are restored when switching pages
    # "No" selected on first page, "Yes" on second
    as_parent.click('input[value="No"]')
    as_parent.click('button:contains(Continue)')
    as_parent.assert_text_visible("second page")
    as_parent.click('input[value="Yes"]')

    as_parent.click('button:contains(Back)')
    as_parent.assert_text_visible("first page")
    as_parent.assert_attribute('input[value="No"]', 'checked')
    as_parent.click('button:contains(Continue)')
    as_parent.assert_text_visible("second page")
    as_parent.assert_attribute('input[value="Yes"]', 'checked')


def test_required_question(survey, parent_open_survey):
    survey.content['pages'][0]['questions'][0]['required'] = True
    survey.save()

    as_parent = parent_open_survey()

    # proceeding to the next page should be impossible without answering a required question
    as_parent.click('button:contains(Continue)')
    as_parent.assert_text_visible("first page")

    # but it should still work after answering
    as_parent.click('input[value="No"]')
    as_parent.click('button:contains(Continue)')
    as_parent.assert_text_visible("second page")


def test_survey_response(parent_open_survey, apps, as_admin):
    as_parent = parent_open_survey()

    as_parent.click('input[value="Yes"]')
    as_parent.click('button:contains(Continue)')
    as_parent.click('input[value="No"]')
    as_parent.click('button:contains(Send)')

    # wait for backend request
    time.sleep(0.1)

    SurveyResponse = apps.lab.get_model('survey_admin', 'SurveyResponse')
    assert SurveyResponse.objects.count() == 1

    # check that you cannot complete the survey a second time
    as_parent = parent_open_survey()
    as_parent.assert_text_visible('already completed')

    # cleanup response
    SurveyResponse.objects.all().delete()


def test_survey_response_restore(parent_open_survey, apps, as_admin):
    as_parent = parent_open_survey()

    as_parent.click('input[value="Yes"]')
    as_parent.click('button:contains("Save for later")')

    # wait for backend request
    time.sleep(0.1)

    # checkbox should be checked when the survey is opened again
    as_parent = parent_open_survey()
    as_parent.assert_attribute('input[value="Yes"]', 'checked')

    # cleanup response
    SurveyResponse = apps.lab.get_model('survey_admin', 'SurveyResponse')
    SurveyResponse.objects.all().delete()
