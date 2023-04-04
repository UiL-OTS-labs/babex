from django.urls import include, path
from rest_framework.routers import DefaultRouter

from mailauth.views import MailAuthView, SetParticipantView
from signups.views import SignupVerifyView

from .views import (
    AppointmentsView,
    GatewayHome,
    Signups,
    SurveyInvitesView,
    SurveyResponseView,
    SurveyView,
)

app_name = "gateway"

router = DefaultRouter()
router.register("signup", Signups, basename="signup")

urlpatterns = [
    path("", GatewayHome.as_view(), name="home"),
    path("", include(router.urls)),
    #
    path("signup/verify/<str:token>/", SignupVerifyView.as_view()),
    #
    path("mailauth/", MailAuthView.as_view()),
    path("mailauth/set_participant/", SetParticipantView.as_view()),
    path("mailauth/token/<str:token>/", MailAuthView.as_view()),
    #
    path("appointment/", AppointmentsView.as_view()),
    #
    path("survey_invites/", SurveyInvitesView.as_view()),
    path("survey/response/", SurveyResponseView.as_view()),
    path("survey/<int:invite_id>/", SurveyView.as_view()),
]
