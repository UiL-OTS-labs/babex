from django.conf.urls import url
from .views import LeaderHomeView


app_name = 'leaders'

urlpatterns = [
    url(r'^$', LeaderHomeView.as_view(), name='home'),
]
