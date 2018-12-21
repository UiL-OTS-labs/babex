from django.urls import path

from experiments.views import (AddExistingCriteriumToExperimentView,
                               CriteriaListView,
                               DefaultCriteriaUpdateView,
                               RemoveCriteriumFromExperiment,
                               )

urlpatterns = [
    path(
        'default_criteria/',
        DefaultCriteriaUpdateView.as_view(),
        name='default_criteria'
    ),

    path(
        'criteria/',
        CriteriaListView.as_view(),
        name='specific_criteria'
    ),
    path(
        'criteria/remove/<int:criterium>/',
        RemoveCriteriumFromExperiment.as_view(),
        name='remove_criterium_from_experiment'
    ),
    path(
        'criteria/add/',
        AddExistingCriteriumToExperimentView.as_view(),
        name='add_criterium_to_experiment'
    ),
]
