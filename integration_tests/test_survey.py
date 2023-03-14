import re
from datetime import date

import pytest


@pytest.fixture(scope='module')
def participant(apps):
    Participant = apps.lab.get_model("participants", "Participant")
    participant = Participant.objects.create(
        email="baby@baby.com",
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
    return participant


@pytest.fixture
def as_parent(sb, apps, participant, mailbox):
    # try to login via email
    sb.switch_to_default_driver()
    sb.open(apps.parent.url)
    sb.type('input[name="email"]', participant.email)
    sb.click('button:contains("Send")')

    mail = mailbox(participant.email)
    assert len(mail)
    html = mail[0].get_payload()[1].get_payload()
    # find link in email
    link = re.search(r'<a href="([^"]+)"', html).group(1)
    sb.open(link)
    return sb


def test_survey_invite(sb, apps, as_admin, participant, mailbox):
    SurveyDefinition = apps.lab.get_model("survey_admin", "SurveyDefinition")
    survey_def = {
        "pages": [
            {"questions": [{"template": "yesno", "prompt": "this is a test question"}]}
        ]
    }
    SurveyDefinition.objects.create(name="Test Survey", content=survey_def)

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


def test_survey_pages(as_parent, apps, as_admin, participant):
    SurveyDefinition = apps.lab.get_model("survey_admin", "SurveyDefinition")
    survey_def = {
        "pages": [
            {"intro": "first page", "questions": [{"template": "yesno", "prompt": "this is a test question"}]},
            {"intro": "second page", "questions": [{"template": "yesno", "prompt": "this is another test question"}]}
        ]
    }
    sd = SurveyDefinition.objects.create(name="Test Survey", content=survey_def)
    sd.surveyinvite_set.create(survey=sd, participant=participant)

    as_parent.open(apps.parent.url + f'/survey/{sd.pk}')

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


def test_required_question(as_parent, apps, as_admin, participant):
    SurveyDefinition = apps.lab.get_model("survey_admin", "SurveyDefinition")
    survey_def = {
        "pages": [
            {"intro": "first page", "questions": [{"template": "yesno", "prompt": "this is a test question", "required": True}]},
            {"intro": "second page", "questions": [{"template": "yesno", "prompt": "this is another test question"}]}
        ]
    }
    sd = SurveyDefinition.objects.create(name="Test Survey", content=survey_def)
    sd.surveyinvite_set.create(participant=participant)

    as_parent.open(apps.parent.url + f'/survey/{sd.pk}')

    # proceeding to the next page should be impossible without answering a required question
    as_parent.click('button:contains(Continue)')
    as_parent.assert_text_visible("first page")

    # but it should still work after answering
    as_parent.click('input[value="No"]')
    as_parent.click('button:contains(Continue)')
    as_parent.assert_text_visible("second page")
