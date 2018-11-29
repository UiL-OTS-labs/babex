from django.conf.urls import url, include
from .views import (ExperimentHomeView, ExperimentCreateView,
                    LocationHomeView, LocationCreateView, UpdateLocationView,
                    DefaultCriteriaUpdateView)


app_name = 'experiments'

urlpatterns = [
    url(r'^$', ExperimentHomeView.as_view(), name='home'),
    url(r'^new/$', ExperimentCreateView.as_view(), name='create'),
    url(r'^(?P<experiment>\d+)/default_criteria/$', DefaultCriteriaUpdateView.as_view(), name='default_criteria'),

    url(r'^locations/', include([
        url(r'^$', LocationHomeView.as_view(), name='location_home'),
        url(r'^new/$', LocationCreateView.as_view(), name='location_create'),
        url(r'^(?P<pk>\d+)/$', UpdateLocationView.as_view(), name='location_update')
    ])),
]
