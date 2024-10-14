from django.urls import path

from .views import (
    DemographicsDataView,
    ExtraDataAddView,
    ParticipantDeleteView,
    ParticipantDetailView,
    ParticipantListDataView,
    ParticipantsDemographicsView,
    ParticipantsHomeView,
    ParticipantUpdateView,
)

app_name = "participants"

urlpatterns = [
    path("", ParticipantsHomeView.as_view(), name="home"),
    path("list/", ParticipantListDataView.as_view(), name="datalist"),
    path("demographics/data/", DemographicsDataView.as_view(), name="demographics_data"),
    path("demographics/", ParticipantsDemographicsView.as_view(), name="demographics"),
    path("<int:pk>/", ParticipantDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", ParticipantUpdateView.as_view(), name="edit"),
    path("<int:pk>/del/", ParticipantDeleteView.as_view(), name="delete"),
    path("<int:pk>/extradata/add", ExtraDataAddView.as_view(), name="extradata.add"),
]
