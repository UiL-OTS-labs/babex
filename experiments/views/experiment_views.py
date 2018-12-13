from django.views import generic
from django.db.models import Sum, Count, Q, F
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy as reverse
from django.utils.translation import ugettext_lazy as _
import braces.views as braces

from ..models import Experiment
from ..forms import ExperimentForm
from .mixins import ExperimentObjectMixin

from uil.core.views.mixins import RedirectSuccessMessageMixin, \
    DeleteSuccessMessageMixin
from uil.core.views import RedirectActionView


# --------------------------------------
# List, create, update and delete views
# --------------------------------------

class ExperimentHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'experiments/index.html'
    model = Experiment

    def get_queryset(self):
        qs = self.model.objects.select_related('location')

        sum_places = Sum('timeslot__max_places')
        count_participants = Count('timeslot__appointments')
        count_excluded_experiments = Count('excluded_experiments')

        return qs.annotate(
            n_places=sum_places,
            n_participants=count_participants,
            n_excluded_experiments=count_excluded_experiments,
        )


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


class ExperimentDeleteView(braces.LoginRequiredMixin, DeleteSuccessMessageMixin,
                           generic.DeleteView):
    model = Experiment
    success_url = reverse('experiments:home')
    template_name = 'experiments/delete.html'
    success_message = _('experiments:message:deleted_experiment')


# --------------------------------------
# Experiment special aspect views
# --------------------------------------

class ExperimentEditExcludedExperimentsView(braces.LoginRequiredMixin,
                                            generic.ListView):
    template_name = 'experiments/excluded_experiments.html'
    model = Experiment

    def get_queryset(self):
        return Experiment.objects.exclude(pk=self.kwargs['experiment'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ExperimentEditExcludedExperimentsView, self) \
            .get_context_data(object_list=object_list, **kwargs)

        context['current_experiment'] = Experiment.objects.get(
            pk=self.kwargs['experiment']
        )

        return context


class ExperimentExcludeOtherExperimentView(braces.LoginRequiredMixin,
                                           RedirectSuccessMessageMixin,
                                           ExperimentObjectMixin,
                                           RedirectActionView):
    experiment_kwargs_name = 'current_experiment'

    def action(self, request):
        exclude_experiment_pk = self.kwargs.get('exclude_experiment')

        current_experiment = self.experiment
        exclude_experiment = Experiment.objects.get(pk=exclude_experiment_pk)

        if exclude_experiment in current_experiment.excluded_experiments.all():
            current_experiment.excluded_experiments.remove(exclude_experiment)
            self.success_message = _('experiments:message:exclude:included')
        else:
            current_experiment.excluded_experiments.add(exclude_experiment)
            self.success_message = _('experiments:message:exclude:excluded')

        current_experiment.save()

    def get_redirect_url(self, *args, **kwargs):
        return reverse('experiments:excluded_experiments', args=[
            self.experiment.pk])


# -------------------
# Action views
# -------------------

class ExperimentSwitchOpenView(braces.LoginRequiredMixin,
                               RedirectSuccessMessageMixin,
                               ExperimentObjectMixin,
                               RedirectActionView):
    experiment_kwargs_name = 'pk'
    url = reverse('experiments:home')

    def action(self, request):

        if self.experiment.open:
            self.experiment.open = False
            self.success_message = _('experiments:message:switch_open:closed')
        else:
            self.experiment.open = True
            self.success_message = _('experiments:message:switch_open:opened')

        self.experiment.save()


class ExperimentSwitchPublicView(braces.LoginRequiredMixin,
                                 RedirectSuccessMessageMixin,
                                 ExperimentObjectMixin,
                                 RedirectActionView):
    experiment_kwargs_name = 'pk'
    url = reverse('experiments:home')

    def action(self, request):
        if self.experiment.public:
            self.experiment.public = False
            self.success_message = _('experiments:message:switch_public:closed')
        else:
            self.experiment.public = True
            self.success_message = _('experiments:message:switch_public:opened')

        self.experiment.save()


class ExperimentSwitchVisibleView(braces.LoginRequiredMixin,
                                  RedirectSuccessMessageMixin,
                                  ExperimentObjectMixin,
                                  RedirectActionView):
    experiment_kwargs_name = 'pk'
    url = reverse('experiments:home')

    def action(self, request):
        if self.experiment.participants_visible:
            self.experiment.participants_visible = False
            self.success_message = _(
                'experiments:message:switch_visible:invisible'
            )
        else:
            self.experiment.participants_visible = True
            self.success_message = _(
                'experiments:message:switch_visible:visible'
            )

        self.experiment.save()

