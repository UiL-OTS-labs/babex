from django.conf.urls import url
from .views import ExperimentHomeView


app_name = 'experiments'

urlpatterns = [
    url(r'^$', ExperimentHomeView.as_view(), name='home'),
]
