from django.urls import path

from experiments.views import (ExperimentCreateView,
                               ExperimentDeleteView,
                               ExperimentHomeView,
                               ExperimentUpdateView,
                               )

urlpatterns = [
    path('', ExperimentHomeView.as_view(), name='home'),
    path('new/', ExperimentCreateView.as_view(), name='create'),
    path('<int:pk>/', ExperimentUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', ExperimentDeleteView.as_view(),
         name='delete'),
]
