from django.conf.urls import url

from .views import LeaderCreateView, LeaderHomeView, LeaderUpdateView, LeaderDeleteView

app_name = 'leaders'

urlpatterns = [
    url(r'^$', LeaderHomeView.as_view(), name='home'),
    url(r'^new/$', LeaderCreateView.as_view(), name='create'),
    url(r'(?P<pk>\d+)/$', LeaderUpdateView.as_view(), name='update'),
    url(r'(?P<pk>\d+)/delete/$', LeaderDeleteView.as_view(), name='delete')
]
