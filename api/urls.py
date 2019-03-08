from django.urls import include, path

import api.auth.views as auth_views
from api.views import ForgotPasswordView, ResetPasswordView, ValidateTokenView, \
    RegisterView
from .router import router
from .views import AdminView, ChangeLeaderView, ChangePasswordView, \
    LeaderView, SwitchExperimentOpenView, SubscribeToEmaillistView, \
    GetAppointmentTokenView, GetRequiredFields

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', AdminView.as_view()),

    path('experiment/<int:experiment>/switch_open/',
         SwitchExperimentOpenView.as_view()),
    path('experiment/<int:experiment>/register/', RegisterView.as_view()),

    path('leader/', include([
        path('', LeaderView.as_view()),
        path('change/', ChangeLeaderView.as_view()),
    ])),

    path('account/', include([
        path('change_password/', ChangePasswordView.as_view()),
        path('forgot_password/', ForgotPasswordView.as_view()),
        path('validate_token/', ValidateTokenView.as_view()),
        path('reset_password/', ResetPasswordView.as_view()),
    ])),

    path('participant/', include([
        path('subscribe_mailinglist/', SubscribeToEmaillistView.as_view()),
        path('send_cancel_token/', GetAppointmentTokenView.as_view()),
        path(
            'get_required_fields/<int:experiment>/',
            GetRequiredFields.as_view(),
        ),
    ])),

    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),
    path('auth/', auth_views.ApiLoginView.as_view())
]
