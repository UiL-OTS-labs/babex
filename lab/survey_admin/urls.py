from django.urls import path

from .views import SurveyOverview, SurveyPreview

app_name = 'survey_admin'

urlpatterns = [
    path('preview/<int:pk>/', SurveyPreview.as_view(), name='preview'),
    path('', SurveyOverview.as_view(), name='overview')
]
