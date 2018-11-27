from django.conf.urls import url
from .views import ExperimentHomeView, CreateExperimentView


app_name = 'experiments'

urlpatterns = [
    url(r'^$', ExperimentHomeView.as_view(), name='home'),
    url(r'^new/$', CreateExperimentView.as_view(), name='create'),
]
