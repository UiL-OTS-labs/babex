from django.urls import path

from .views import ExtraDataAddView, ParticipantDeleteView, ParticipantDetailView, \
    ParticipantSpecificCriteriaUpdateView, \
    ParticipantUpdateView, ParticipantsHomeView, \
    ParticipantsDemographicsView, render_demograhpics_png, render_demograhpics_svg

app_name = 'participants'

urlpatterns = [
    path('', ParticipantsHomeView.as_view(), name='home'),
    path("demographics/", ParticipantsDemographicsView.as_view(), name='demographics'),
    path('<int:pk>/', ParticipantDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', ParticipantUpdateView.as_view(), name='edit'),
    path('<int:pk>/del/', ParticipantDeleteView.as_view(), name='delete'),
    path(
        '<int:pk>/specific-criteria/',
        ParticipantSpecificCriteriaUpdateView.as_view(),
        name='update_specific_criteria'
    ),

    path('<int:pk>/extradata/add', ExtraDataAddView.as_view(), name='extradata.add')
]

# paths for the demographics graph urls these render image/png or similar
graphpatterns = [
    path("demographics/png/", render_demograhpics_png, name='histo-png'),
    path("demographics/png/<int:width>/", render_demograhpics_png, name='histo-png'),
    path("demographics/svg/", render_demograhpics_svg, name='histo-svg'),
    path("demographics/svg/<int:width>/", render_demograhpics_svg, name='histo-svg'),
]

urlpatterns += graphpatterns
