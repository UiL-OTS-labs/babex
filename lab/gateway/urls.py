from django.urls import include, path
from rest_framework.routers import DefaultRouter

from mailauth.views import MailAuthView, SetParticipantView
from signups.views import SignupVerifyView

from . import views

app_name = "gateway"

router = DefaultRouter()
router.register("signup", views.Signups, basename="signup")
router.register("survey", views.SurveyViewSet, basename="survey")
router.register("appointment", views.AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("", views.GatewayHome.as_view(), name="home"),
    path("", include(router.urls)),
    #
    path("signup/verify/<str:token>/", SignupVerifyView.as_view()),
    #
    path("mailauth/", MailAuthView.as_view()),
    path("mailauth/set_participant/", SetParticipantView.as_view()),
    path("mailauth/token/<str:token>/", MailAuthView.as_view()),
    #
    path("survey_invites/", views.SurveyInvitesView.as_view()),
    #
    path("deactivate/", views.DeactivateView.as_view()),
]
