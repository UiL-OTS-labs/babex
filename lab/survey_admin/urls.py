from django.urls import path

from .views import SurveyInviteParticipants, SurveyOverview, SurveyPreview

app_name = "survey_admin"

urlpatterns = [
    path("preview/<int:pk>/", SurveyPreview.as_view(), name="preview"),
    path("invite/<int:pk>/", SurveyInviteParticipants.as_view(), name="invite"),
    path("", SurveyOverview.as_view(), name="overview"),
]
