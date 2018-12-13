from django.conf.urls import url
from .views import ParticipantsHomeView, ParticipantDetailView, \
    ParticipantUpdateView, ParticipantDeleteView, \
    ParticipantSpecificCriteriaUpdateView, ParticipantMergeView


app_name = 'participants'

urlpatterns = [
    url(r'^$', ParticipantsHomeView.as_view(), name='home'),
    url(r'^(?P<pk>\d+)/$', ParticipantDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/edit/$', ParticipantUpdateView.as_view(), name='edit'),
    url(r'^(?P<pk>\d+)/del/$', ParticipantDeleteView.as_view(), name='delete'),
    url(
        r'^(?P<pk>\d+)/specific-criteria/$',
        ParticipantSpecificCriteriaUpdateView.as_view(),
        name='update_specific_criteria'
    ),
    url(r'^merge/$', ParticipantMergeView.as_view(), name='merge'),
]
