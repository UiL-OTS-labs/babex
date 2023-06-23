from django.urls import path

from experiments.views import (
    ExperimentAppointmentsView,
    InviteParticipantsForExperimentView,
    MailPreviewView,
)

urlpatterns = [
    path(
        "participants/",
        ExperimentAppointmentsView.as_view(),
        name="participants",
    ),
    path(
        "invite/",
        InviteParticipantsForExperimentView.as_view(),
        name="invite",
    ),
    path(
        "invite/preview/",
        MailPreviewView.as_view(),
        name="mail_preview",
    ),
]
