from django.urls import path

from .views import ParticipantDeleteView, ParticipantDetailView, \
    ParticipantMergeView, ParticipantSpecificCriteriaUpdateView, \
    ParticipantUpdateView, ParticipantsHomeView

app_name = 'participants'

urlpatterns = [
    path('', ParticipantsHomeView.as_view(), name='home'),
    path('<int:pk>/', ParticipantDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', ParticipantUpdateView.as_view(), name='edit'),
    path('<int:pk>/del/', ParticipantDeleteView.as_view(), name='delete'),
    path(
        '<int:pk>/specific-criteria/',
        ParticipantSpecificCriteriaUpdateView.as_view(),
        name='update_specific_criteria'
    ),
    path('merge/', ParticipantMergeView.as_view(), name='merge'),
]
