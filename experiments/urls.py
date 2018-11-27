from django.conf.urls import url, include
from .views import (ExperimentHomeView, CreateExperimentView,
                    LocationHomeView, CreateLocationView, UpdateLocationView,
                    UpdateDefaultCriteriaView)


app_name = 'experiments'

urlpatterns = [
    url(r'^$', ExperimentHomeView.as_view(), name='home'),
    url(r'^new/$', CreateExperimentView.as_view(), name='create'),
    url(r'^(?P<experiment>\d+)/default_criteria/$', UpdateDefaultCriteriaView.as_view(), name='default_criteria'),

    url(r'^locations/', include([
        url(r'^$', LocationHomeView.as_view(), name='location_home'),
        url(r'^new/$', CreateLocationView.as_view(), name='location_create'),
        url(r'^(?P<pk>\d+)/$', UpdateLocationView.as_view(), name='location_update')
    ])),
]
