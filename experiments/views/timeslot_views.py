from django.views import generic
from django.urls import reverse
import braces.views as braces

from ..models import TimeSlot, Experiment
from .mixins import ExperimentObjectMixin


class TimeSlotHomeView(braces.LoginRequiredMixin,
                       ExperimentObjectMixin, generic.ListView):
    template_name = 'timeslots/index.html'
    model = TimeSlot

    def get_queryset(self):
        return self.model.objects.filter(experiment=self.experiment)

    def get_context_data(self, *_, **kwargs):
        context = super(TimeSlotHomeView, self).get_context_data(**kwargs)

        context['experiment'] = self.experiment

        return context
