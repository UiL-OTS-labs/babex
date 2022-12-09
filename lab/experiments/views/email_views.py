import braces.views as braces
from cdh.core.mail import BaseEmailPreviewView
from django.http.response import HttpResponse

from ..email import AppointmentConfirmEmail
from .mixins import ExperimentObjectMixin


def email_preview_view(request, pk):
    return HttpResponse('yo')


class AppointmentConfirmEmailPreview(braces.LoginRequiredMixin, ExperimentObjectMixin, BaseEmailPreviewView):
    email_class = AppointmentConfirmEmail

    def post(self, request, experiment):
        return super().post(request)

    def get_preview_context(self):
        return {
            'date': '2022-01-01',
            'time': '10:00',
            'experiment_name': 'Experiment Name',
            'experiment_location': 'Location',
            'participant_name': 'Participant Name',
            'leader_name': 'Leader Name',
            'leader_email': 'leader@uu.nl',
            'leader_phonenumber': '064-12345678',
            'all_leaders_name_list': 'First Leader en Second Leader'
        }
