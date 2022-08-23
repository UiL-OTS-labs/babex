import braces.views as braces
from django.views import generic

from experiments.models import Experiment

from django.db.models import Count, Sum
from django.db.models.functions import Now


class HomeView(braces.LoginRequiredMixin, generic.TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context['experiments'] = self._get_experiments()

        return context

    def _get_free_slots(self):
        qs = Experiment.objects.filter(open=True).select_related(
            'location').filter(timeslot__datetime__gte=Now())

        sum_places = Sum('timeslot__max_places')
        count_participants = Count('timeslot__appointments')

        experiments = qs.annotate(
            n_places=sum_places,
            n_participants=count_participants,
        )

        free_slots = 0

        for experiment in experiments:
            free_slots += experiment.n_places - experiment.n_participants

        return free_slots

    def _get_experiments(self):
        return Experiment.objects.filter(open=True)
