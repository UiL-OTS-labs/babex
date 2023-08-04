from secrets import token_urlsafe

import cdh.core.fields as e_fields
from cdh.core.mail import TemplateEmail
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Signup(models.Model):
    name = e_fields.EncryptedCharField(max_length=100)
    sex = e_fields.EncryptedCharField(max_length=50)
    birth_date = e_fields.EncryptedDateField()

    parent_name = e_fields.EncryptedTextField()
    phonenumber = e_fields.EncryptedTextField()
    phonenumber_alt = e_fields.EncryptedTextField(blank=True)
    email = e_fields.EncryptedTextField()

    english_contact = e_fields.EncryptedBooleanField()
    newsletter = e_fields.EncryptedBooleanField()

    dyslexic_parent = e_fields.EncryptedCharField(max_length=5)
    multilingual = e_fields.EncryptedBooleanField()

    birth_weight = e_fields.EncryptedIntegerField(_("participant:attribute:birth_weight"))
    pregnancy_weeks = e_fields.EncryptedIntegerField(_("participant:attribute:pregnancy_weeks"))
    pregnancy_days = e_fields.EncryptedIntegerField(_("participant:attribute:pregnancy_days"))

    class Status(models.TextChoices):
        NEW = "NEW", _("signups:stats:new")
        APPROVED = "APPROVED", _("signups:stats:approved")
        REJECTED = "REJECTED", _("signups:stats:rejected")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    created = models.DateTimeField(auto_now_add=True)
    email_verified = models.DateTimeField(null=True, blank=True)
    link_token = models.CharField(max_length=64, default=token_urlsafe, unique=True)

    def send_email_validation(self):
        mail = TemplateEmail(
            html_template="signups/mail/validation.html",
            context=dict(
                base_url=settings.PARENT_URI,
                link_token=self.link_token,
            ),
            to=[self.email],
            subject="please validate your email",
        )
        mail.send()
