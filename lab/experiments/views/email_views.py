from datetime import datetime

import braces.views as braces
from cdh.core.mail import BaseEmailPreviewView
from django.template import defaultfilters

from main.auth.util import RandomLeaderMixin

from ..email import AppointmentConfirmEmail
from ..models import Experiment
from .mixins import ExperimentObjectMixin


def sample_context(experiment: Experiment):
    return {
        "date": defaultfilters.date(datetime.now(), "l d-m-Y"),
        "time": defaultfilters.date(datetime.now(), "H:i"),
        "experiment_name": experiment.name,
        "experiment_location": experiment.location.name if experiment.location is not None else "-",
        "participant_name": "Participant Name",
        "leader_name": "Leader Name",
        "leader_email": "leader@uu.nl",
        "leader_phonenumber": "064-12345678",
        "all_leaders_name_list": "First Leader en Second Leader",
        "duration": experiment.duration,
        "compensation": experiment.compensation,
        "task_description": experiment.task_description,
        "additional_instructions": experiment.additional_instructions,
    }


class AppointmentConfirmEmailPreview(RandomLeaderMixin, ExperimentObjectMixin, BaseEmailPreviewView):
    email_class = AppointmentConfirmEmail

    def post(self, request, **kwargs):
        return super().post(request)

    def get_preview_context(self):
        return sample_context(self.experiment)


class InviteEmailPreview(RandomLeaderMixin, ExperimentObjectMixin, BaseEmailPreviewView):
    email_class = AppointmentConfirmEmail

    def post(self, request, **kwargs):
        return super().post(request)

    def get_preview_context(self):
        return sample_context(self.experiment)


def email_preview(request, template, experiment):
    if template == "confirmation":
        return AppointmentConfirmEmailPreview.as_view()(request, experiment=experiment)
    elif template == "invite":
        return InviteEmailPreview.as_view()(request, experiment=experiment)
