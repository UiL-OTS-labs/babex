from django.conf.urls import url
from .views import ParticipantsHomeView, ParticipantDetailView, \
    ParticipantUpdateView


app_name = 'participants'

urlpatterns = [
    url(r'^$', ParticipantsHomeView.as_view(), name='home'),
    url(r'^(?P<pk>\d+)/$', ParticipantDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/edit/$', ParticipantUpdateView.as_view(), name='edit'),
]
