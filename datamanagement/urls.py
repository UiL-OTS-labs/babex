from django.urls import path

from .views import HideParticipantsView, OverviewView, DeleteInvitesView, \
    ThresholdsEditView, DeleteParticipantView

app_name = 'datamanagement'

urlpatterns = [
    path('', OverviewView.as_view(), name='overview'),
    path('edit_thresholds/', ThresholdsEditView.as_view(), name='thresholds'),

    path('<int:participant>/delete/',
         DeleteParticipantView.as_view(),
         name="delete_participant"),

    path('<int:experiment>/hide_participants/',
         HideParticipantsView.as_view(),
         name='hide_participants'),
    path('<int:experiment>/delete_invites/',
         DeleteInvitesView.as_view(),
         name='delete_invites'),
]
