from datetime import datetime, timedelta

from cdh.core.mail import TemplateEmail
from django.conf import settings
from django.db import models

from mailauth.models import create_mail_auth
from participants.models import Participant


class SurveyDefinition(models.Model):
    name = models.CharField(max_length=200)

    content = models.JSONField()


class SurveyInvite(models.Model):
    survey = models.ForeignKey(SurveyDefinition, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="survey_invites")
    created = models.DateTimeField(auto_now_add=True)
    completed = models.DateTimeField(null=True)

    class Meta:
        unique_together = ["survey", "participant"]

    def send(self):
        expiry = datetime.now() + timedelta(days=7)
        mauth = create_mail_auth(expiry, participant=self.participant)

        context = dict(link=mauth.get_link(f"survey/{self.survey.pk}"))
        mail = TemplateEmail(
            html_template="survey_admin/mail/invite.html",
            context=context,
            to=[self.participant.email],
            subject="invitation to fill survey",
        )
        mail.send()
