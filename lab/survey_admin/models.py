from datetime import datetime, timedelta

from cdh.mail.classes import TemplateEmail
from django.db import models
from django.utils import translation

from mailauth.models import create_mail_auth
from participants.models import Participant


class SurveyDefinition(models.Model):
    name = models.CharField(max_length=200)

    content = models.JSONField()


class SurveyInvite(models.Model):
    survey = models.ForeignKey(SurveyDefinition, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="survey_invites")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # TODO: should these be unique together? maybe a participant can fill the same survey
        # multiple times?
        unique_together = ["survey", "participant"]

    def get_link(self):
        expiry = datetime.now() + timedelta(days=7)
        mauth = create_mail_auth(expiry, participant=self.participant)

        return mauth.get_link(f"/survey/{self.pk}")

    def send(self):
        context = dict(link=self.get_link())
        with translation.override("nl"):
            mail = TemplateEmail(
                html_template="survey_admin/mail/invite.html",
                context=context,
                to=[self.participant.email],
                subject="invitation to fill survey",
            )
            mail.send()


class SurveyResponse(models.Model):
    invite = models.OneToOneField(SurveyInvite, on_delete=models.CASCADE)
    data = models.JSONField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    completed = models.DateTimeField(null=True)

    # for partial responses: store the index of the page from which we should resume the survey
    page = models.IntegerField(default=0)
