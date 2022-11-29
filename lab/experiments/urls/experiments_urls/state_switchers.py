from django.urls import path

from experiments.views import (ExperimentSwitchOpenView,
                               ExperimentSwitchPublicView,)

urlpatterns = [
    path('switch_open/', ExperimentSwitchOpenView.as_view(),
         name='switch_open'),
    path('switch_public/', ExperimentSwitchPublicView.as_view(),
         name='switch_public'),
]
