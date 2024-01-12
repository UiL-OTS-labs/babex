from typing import List

from ..models import Experiment


class ExperimentObjectMixin:
    """
    This mixin adds a new property to a view, which contains an experiment
    object.

    It does this by defining a cached property method, which looks up the
    experiment pk form self.kwargs, and returns the appropriate Experiment
    object.

    One can set the kwargs variable name with the 'experiment_kwargs_name'
    class variable, which defaults to 'experiment'. (Not pk, as in those
    cases the default views provides the self.object variable).
    """

    experiment_kwargs_name = "experiment"

    experiment_select_related: List[str] = []
    experiment_prefetch_related: List[str] = []

    @property
    def experiment(self):
        pk = self.kwargs.get(self.experiment_kwargs_name)

        qs = Experiment.objects.get_queryset()

        if self.experiment_select_related:
            qs = qs.select_related(*self.experiment_select_related)

        if self.experiment_prefetch_related:
            qs = qs.prefetch_related(*self.experiment_prefetch_related)

        return qs.get(pk=pk)
