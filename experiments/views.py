from django.views import generic
import braces.views as braces

from .models import Experiment


class ExperimentHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'experiments/index.html'
    model = Experiment
