from django.conf.urls import url
from .views import LeaderHomeView, LeaderCreateView, LeaderUpdateView


app_name = 'leaders'

urlpatterns = [
    url(r'^$', LeaderHomeView.as_view(), name='home'),
    url(r'^new/$', LeaderCreateView.as_view(), name='create'),
    url(r'(?P<pk>\d+)/', LeaderUpdateView.as_view(), name='update'),
]
