from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy as reverse
from django.utils.translation import ugettext_lazy as _
import braces.views as braces

from main.views import RedirectSuccessMessageMixin
from ..models import Experiment
from ..forms import ExperimentForm


class ExperimentHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'experiments/index.html'
    model = Experiment


class ExperimentCreateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                           generic.CreateView):
    template_name = 'experiments/new.html'
    form_class = ExperimentForm
    success_message = _('experiments:message:create:success')

    def get_success_url(self):
        return reverse('experiments:default_criteria', args=[self.object.pk])


class ExperimentUpdateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                           generic.UpdateView):
    template_name = 'experiments/edit.html'
    form_class = ExperimentForm
    model = Experiment
    success_message = _('experiments:message:update:success')
    success_url = reverse('experiments:home')


class ExperimentSwitchOpenView(braces.LoginRequiredMixin,
                               RedirectSuccessMessageMixin,
                               generic.RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get('pk')

        experiment = Experiment.objects.get(pk=pk)

        if experiment.open:
            experiment.open = False
            self.success_message = _('experiments:message:switch_open:closed')
        else:
            experiment.open = True
            self.success_message = _('experiments:message:switch_open:opened')

        experiment.save()

        return reverse('experiments:home')


class ExperimentSwitchPublicView(braces.LoginRequiredMixin,
                                 RedirectSuccessMessageMixin,
                                 generic.RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get('pk')

        experiment = Experiment.objects.get(pk=pk)

        if experiment.public:
            experiment.public = False
            self.success_message = _('experiments:message:switch_public:closed')
        else:
            experiment.public = True
            self.success_message = _('experiments:message:switch_public:opened')

        experiment.save()

        return reverse('experiments:home')


class ExperimentSwitchVisibleView(braces.LoginRequiredMixin,
                                  RedirectSuccessMessageMixin,
                                  generic.RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs.get('pk')

        experiment = Experiment.objects.get(pk=pk)

        if experiment.participants_visible:
            experiment.participants_visible = False
            self.success_message = _(
                'experiments:message:switch_visible:visible'
            )
        else:
            experiment.participants_visible = True
            self.success_message = _(
                'experiments:message:switch_visible:invisible'
            )

        experiment.save()

        return reverse('experiments:home')

