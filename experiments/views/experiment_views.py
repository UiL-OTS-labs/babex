from django.views import generic
from django.urls import reverse
import braces.views as braces

from ..models import Experiment
from ..forms import CreateExperimentForm


class ExperimentHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'experiments/index.html'
    model = Experiment


class CreateExperimentView(braces.LoginRequiredMixin, generic.CreateView):
    template_name = 'experiments/new.html'
    form_class = CreateExperimentForm

    def get_success_url(self):
        return reverse('experiments:default_criteria', args=[self.object.pk])
