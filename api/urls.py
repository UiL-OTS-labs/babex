from django.urls import include, path

import api.auth.views as auth_views
from .router import router
from .views import AdminView, ChangeLeaderView, LeaderView, \
    SwitchExperimentOpenView

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', AdminView.as_view()),
    path('experiment/<int:experiment>/switch_open/',
         SwitchExperimentOpenView.as_view()),
    path('leader/', include([
        path('', LeaderView.as_view()),
        path('change/', ChangeLeaderView.as_view()),
    ])),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),
    path('auth/', auth_views.ApiLoginView.as_view())
]
