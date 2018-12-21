from django.urls import path

from experiments.views import (AddExistingCriteriumToExperimentView,
                               CriteriaListView,
                               DefaultCriteriaUpdateView,
                               RemoveCriteriumFromExperiment,
                               )

urlpatterns = [
    path(
        '<int:experiment>/default_criteria/',
        DefaultCriteriaUpdateView.as_view(),
        name='default_criteria'
    ),

    path(
        '<int:experiment>/criteria/',
        CriteriaListView.as_view(),
        name='specific_criteria'
    ),
    path(
        r'<int:experiment>/criteria/remove/<int:criterium>/',
        RemoveCriteriumFromExperiment.as_view(),
        name='remove_criterium_from_experiment'
    ),
    path(
        '<int:experiment>/criteria/add/',
        AddExistingCriteriumToExperimentView.as_view(),
        name='add_criterium_to_experiment'
    ),
]
