from django.contrib import admin
from django.urls import include, path

from .views import (
    SignupDone,
    SignupView,
    home,
    signup_verify,
    status,
    survey_response_view,
    survey_view,
    cancel_appointment_view
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("cdhcore/", include("cdh.core.urls")),
    # home
    path("", home, name="home"),
    path("status", status),
    # magiclink
    path("auth/", include("mailauth.urls")),
    # signup
    path("signup/", SignupView.as_view(), name="signup"),
    path("signup/done", SignupDone.as_view(), name="signup.done"),
    path("signup/verify/<str:token>", signup_verify, name="signup.confirm"),
    # surveys
    path("survey/<int:invite_id>/", survey_view, name="survey"),
    path("survey/response/", survey_response_view, name="survey.response"),
    # appointments
    path("appointment/<int:appointment_id>/cancel/", cancel_appointment_view, name="appointment.cancel"),
]
