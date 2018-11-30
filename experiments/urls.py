from django.conf.urls import url, include
from .views import (ExperimentHomeView, ExperimentCreateView,
                    ExperimentUpdateView,
                    ExperimentSwitchOpenView, ExperimentSwitchVisibleView,
                    ExperimentSwitchPublicView,
                    LocationHomeView, LocationCreateView, UpdateLocationView,
                    DefaultCriteriaUpdateView, )

app_name = 'experiments'

urlpatterns = [
    url(r'^$', ExperimentHomeView.as_view(), name='home'),
    url(r'^new/$', ExperimentCreateView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/$', ExperimentUpdateView.as_view(), name='update'),

    url(r'^(?P<experiment>\d+)/default_criteria/$',
        DefaultCriteriaUpdateView.as_view(), name='default_criteria'),


    url(r'(?P<pk>\d+)/switch_open/', ExperimentSwitchOpenView.as_view(),
        name='switch_open'),
    url(r'(?P<pk>\d+)/switch_visible/', ExperimentSwitchVisibleView.as_view(),
        name='switch_visible'),
    url(r'(?P<pk>\d+)/switch_public/', ExperimentSwitchPublicView.as_view(),
        name='switch_public'),

    url(r'^locations/', include([
        url(r'^$', LocationHomeView.as_view(), name='location_home'),
        url(r'^new/$', LocationCreateView.as_view(), name='location_create'),
        url(r'^(?P<pk>\d+)/$', UpdateLocationView.as_view(),
            name='location_update')
    ])),
]
