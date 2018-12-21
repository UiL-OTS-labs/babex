from django.urls import path

from experiments.views import (ExperimentAppointmentsView,
                               InviteParticipantsForExperimentView,
                               MailPreviewView, )

urlpatterns = [
    path(
        '<int:experiment>/participants/',
        ExperimentAppointmentsView.as_view(),
        name='participants',
    ),

    path(
        '<int:experiment>/invite/',
        InviteParticipantsForExperimentView.as_view(),
        name='invite',
    ),

    path(
        '<int:experiment>/invite/preview/',
        MailPreviewView.as_view(),
        name='mail_preview',
    ),
]
