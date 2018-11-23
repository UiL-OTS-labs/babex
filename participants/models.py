from django.db import models
from django.utils.translation import ugettext_lazy as _

from api.auth.models import ApiUser


class Participant(models.Model):

    HANDEDNESS = (
        ('left', _('participant:attribute:handedness:lefthanded')),
        ('right', _('participant:attribute:handedness:righthanded')),
    )

    # Yes, this is controversial. I'm sorry!
    SEX = (
        ('M', _('participant:attribute:sex:male')),
        ('F', _('participant:attribute:sex:female')),
    )

    SOCIAL_ROLE = (
        ('student', _('participant:attribute:social_role:student')),
        ('other', _('participant:attribute:social_role:other')),
    )

    email = models.EmailField()

    name = models.TextField()

    language = models.TextField()

    dyslexic = models.BooleanField()

    birth_date = models.DateField()

    multilingual = models.BooleanField()

    phonenumber = models.TextField()

    handedness = models.TextField(choices=HANDEDNESS)

    sex = models.TextField(choices=SEX)

    social_role = models.TextField(choices=SOCIAL_ROLE)

    email_subscription = models.BooleanField(default=False)

    capable = models.BooleanField(default=True)

    api_user = models.OneToOneField(ApiUser, null=True, blank=True, on_delete=models.SET_NULL)


class SecondaryEmail(models.Model):
    email = models.EmailField()

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)

