from django.urls import path

from experiments.views import (ExperimentSwitchOpenView,
                               ExperimentSwitchPublicView,
                               ExperimentSwitchVisibleView, )

urlpatterns = [
    path('switch_open/', ExperimentSwitchOpenView.as_view(),
         name='switch_open'),
    path('switch_visible/', ExperimentSwitchVisibleView.as_view(),
         name='switch_visible'),
    path('switch_public/', ExperimentSwitchPublicView.as_view(),
         name='switch_public'),
]
