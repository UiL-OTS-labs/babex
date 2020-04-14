from django.urls import path

from .views import OverviewView, DeleteInvitesView, DeleteCommentsView, ThresholdsEditView

app_name = 'datamanagement'

urlpatterns = [
    path('', OverviewView.as_view(), name='overview'),
    path('edit_thresholds/', ThresholdsEditView.as_view(), name='thresholds'),
    path('delete_invites/<int:experiment>', DeleteInvitesView.as_view(),
         name='delete_invites'),
    path('delete_comments/<int:experiment>', DeleteCommentsView.as_view(),
         name='delete_comments'),
]
