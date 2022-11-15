from django.urls import path

from .views import ParticipantDeleteView, ParticipantDetailView, \
    ParticipantSpecificCriteriaUpdateView, \
    ParticipantUpdateView, ParticipantsHomeView, \
    ParticipantsDemographicsView, render_demograhpics

app_name = 'participants'

DEMO_PATH = "demographics/"

urlpatterns = [
    path('', ParticipantsHomeView.as_view(), name='home'),
    path(DEMO_PATH, ParticipantsDemographicsView.as_view(), name='demographics'), #temporary stub in order to render the menu. Needs new view!
    path('<int:pk>/', ParticipantDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', ParticipantUpdateView.as_view(), name='edit'),
    path('<int:pk>/del/', ParticipantDeleteView.as_view(), name='delete'),
    path(
        '<int:pk>/specific-criteria/',
        ParticipantSpecificCriteriaUpdateView.as_view(),
        name='update_specific_criteria'
    ),
]

# paths for the demographics graph urls these render image/png or similar
graphpatterns = [
    path(DEMO_PATH + "png/", render_demograhpics, name='png'),
]

urlpatterns += graphpatterns
