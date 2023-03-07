import re
from datetime import date


def test_survey_invite(sb, apps, as_admin, mailbox):
    # create some test data
    Participant = apps.lab.get_model('participants', 'Participant')
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

    SurveyDefinition = apps.lab.get_model('survey_admin', 'SurveyDefinition')
    survey_def = dict(
        questions=[
            dict(template='yesno',
                 prompt='this is a test question')
        ])
    SurveyDefinition.objects.create(name='Test Survey', content=survey_def)

    # send survey invite as admin
    sb.switch_to_driver(as_admin)
    sb.click("a:contains(Surveys)")
    sb.click("button.dropdown-toggle")
    sb.click("a:contains(invite)")
    sb.click('input[type="checkbox"]')
    sb.click('button:contains(send)')

    # read survey invite mail
    mail = mailbox(participant.email)
    assert len(mail)
    html = mail[0].get_payload()[1].get_payload()
    # find link in email
    # it should authenticate us an redirect directly to the survey
    link = re.search(r'<a href="([^"]+)"', html).group(1)
    sb.open(link)

    # check that at least the question text is visible
    sb.assert_text_visible('this is a test question')
