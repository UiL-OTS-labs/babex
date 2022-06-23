from django.urls import path

from experiments.views import (AddExistingCriterionToExperimentView,
                               CriteriaListView,
                               DefaultCriteriaUpdateView,
                               RemoveCriterionFromExperiment,
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
        'criteria/remove/<int:criterion>/',
        RemoveCriterionFromExperiment.as_view(),
        name='remove_criterion_from_experiment'
    ),
    path(
        'criteria/add/',
        AddExistingCriterionToExperimentView.as_view(),
        name='add_criterion_to_experiment'
    ),
]
