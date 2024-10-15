from django.urls import path

from experiments.views import (
    ExperimentAppointmentsView,
    InviteParticipantsForExperimentView,
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
]
