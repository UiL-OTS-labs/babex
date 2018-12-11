from django.conf.urls import url
from .views import ParticipantsHomeView, ParticipantDetailView


app_name = 'participants'

urlpatterns = [
    url(r'^$', ParticipantsHomeView.as_view(), name='home'),
    url(r'^(?P<pk>\d+)/$', ParticipantDetailView.as_view(), name='detail'),
]
