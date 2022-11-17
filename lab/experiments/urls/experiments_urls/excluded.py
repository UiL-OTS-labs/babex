from django.urls import path

from experiments.views import ExperimentEditExcludedExperimentsView, \
    ExperimentExcludeOtherExperimentView

urlpatterns = [
    path(
        '<int:experiment>/excluded_experiments/',
        ExperimentEditExcludedExperimentsView.as_view(),
        name='excluded_experiments'
    ),
    path(
        '<int:current_experiment>/exclude_experiment/<int:exclude_experiment>/',
        ExperimentExcludeOtherExperimentView.as_view(),
        name='exclude_experiment'
    ),
]
