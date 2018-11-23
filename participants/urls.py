from django.conf.urls import url
from .views import ParticipantsHomeView


app_name = 'participants'

urlpatterns = [
    url(r'^$', ParticipantsHomeView.as_view(), name='home'),
]
