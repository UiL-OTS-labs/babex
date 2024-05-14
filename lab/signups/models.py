import json
from secrets import token_urlsafe

import cdh.core.fields as e_fields
from cdh.core.fields.mixin import EncryptedMixin
from cdh.mail.classes import TemplateEmail
from django.conf import settings
from django.db import models
from django.utils import translation
from django.utils.translation import gettext_lazy as _


class EncryptedJSONListField(EncryptedMixin, models.JSONField):
    def to_python(self, value):
        decrypted = EncryptedMixin.to_python(self, value)
        if decrypted is None:
            return []
        return json.loads(decrypted, cls=self.decoder)


class Signup(models.Model):
    name = e_fields.EncryptedCharField(max_length=100)
    sex = e_fields.EncryptedCharField(max_length=50)
    birth_date = e_fields.EncryptedDateField()

    parent_first_name = e_fields.EncryptedTextField()
    parent_last_name = e_fields.EncryptedTextField()
    phonenumber = e_fields.EncryptedTextField()
    phonenumber_alt = e_fields.EncryptedTextField(blank=True)

    email = e_fields.EncryptedTextField()

    save_longer = e_fields.EncryptedBooleanField()
    english_contact = e_fields.EncryptedBooleanField()
    newsletter = e_fields.EncryptedBooleanField()

    dyslexic_parent = e_fields.EncryptedCharField(max_length=5)
    tos_parent = e_fields.EncryptedCharField(max_length=5, null=True)

    # why is this a json field?
    # mostly because the user should be able to add their own language,
    # but we don't want to create a model right away because it has to first be approved.
    # upon approval, these will be translated into ForeignKey relations (see Participant.languages)
    languages = EncryptedJSONListField(null=True)

    birth_weight = e_fields.EncryptedCharField(_("participant:attribute:birth_weight"), max_length=30)
    pregnancy_duration = e_fields.EncryptedCharField(
        _("participant:attribute:pregnancy_weeks"), max_length=30, null=True
    )

    class Status(models.TextChoices):
        NEW = "NEW", _("signups:stats:new")
        APPROVED = "APPROVED", _("signups:stats:approved")
        REJECTED = "REJECTED", _("signups:stats:rejected")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    created = models.DateTimeField(auto_now_add=True)
    email_verified = models.DateTimeField(null=True, blank=True)
    link_token = models.CharField(max_length=64, default=token_urlsafe, unique=True)

    def send_email_validation(self):
        with translation.override("nl"):
            mail = TemplateEmail(
                html_template="signups/mail/validation.html",
                context=dict(
                    base_url=settings.PARENT_URI,
                    link_token=self.link_token,
                ),
                to=[self.email],
                subject=_("signups:mail:validation:subject"),
            )
            mail.send()
