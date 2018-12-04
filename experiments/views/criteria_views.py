from django.http import Http404
from django.contrib.messages.views import SuccessMessageMixin
from django.views import generic
from django.urls import reverse_lazy as reverse
from django.utils.translation import ugettext_lazy as _
import braces.views as braces
from uil.core.views.mixins import RedirectSuccessMessageMixin

from ..models import DefaultCriteria, Criterium, Experiment
from ..forms import DefaultCriteriaForm, CriteriumForm, ExperimentCriteriumForm
from main.views import FormListView


#
# Criteria views
#

class CriteriaHomeView(braces.LoginRequiredMixin, generic.ListView):
    model = Criterium
    template_name = 'criteria/index.html'


class CriteriaCreateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                         generic.CreateView):
    form_class = CriteriumForm
    template_name = 'criteria/new.html'
    success_url = reverse('experiments:criteria_home')
    success_message = _('criteria:messages:created')


class CriteriaUpdateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                         generic.UpdateView):
    form_class = CriteriumForm
    template_name = 'criteria/edit.html'
    success_url = reverse('experiments:criteria_home')
    success_message = _('criteria:messages:updated')
    model = Criterium


#
# Experiment Criteria views
#


class DefaultCriteriaUpdateView(braces.LoginRequiredMixin, generic.UpdateView):
    template_name = 'criteria/update_default.html'
    form_class = DefaultCriteriaForm
    model = DefaultCriteria

    pk_url_kwarg = 'experiment'

    def get_object(self, queryset=None):
        """
        Overrides the default get_object because that one assumes that we we
        always use the pk to get the object _for some reason_
        """

        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg)

        kwargs = {
            self.pk_url_kwarg: pk
        }

        if pk is not None:
            queryset = queryset.filter(**kwargs)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {
                              'verbose_name': queryset.model._meta.verbose_name
                          })
        return obj

    def get_success_url(self):
        return reverse('experiments:home')


class CriteriaListView(braces.LoginRequiredMixin, SuccessMessageMixin,
                       FormListView):
    """
    This view is a bit special, it's both a ListView and a CreateView in one!
    In addition, there is a second form in the template that POSTs to the
    AddExistingCriteriumToExperimentView view (below).

    The get_initial and get_success_url are for the CreateView, the get_queryset
    is for the ListView and get_context_data is used for the second manual form.
    """
    template_name = 'criteria/specific_list.html'
    model = Criterium
    form_class = ExperimentCriteriumForm
    success_message = _('criteria:messages:created_and_added')

    def get_initial(self):
        """This makes sure that the add_criteria also adds it to the
        experiment, by adding the experiment to the hidden experiments field.
        """
        initial = super(CriteriaListView, self).get_initial()

        experiment = Experiment.objects.get(pk=self.kwargs.get('experiment'))

        initial['experiments'] = [experiment]

        return initial

    def get_success_url(self):
        args = [self.kwargs.get('experiment')]
        return reverse('experiments:specific_criteria', args=args)

    def get_context_data(self, **kwargs):
        context = super(CriteriaListView, self).get_context_data(**kwargs)

        context['criteria_options'] = self.model.objects.exclude(
            id__in=self.get_queryset()
        )

        experiment_pk = self.kwargs['experiment']
        context['experiment'] = Experiment.objects.get(pk=experiment_pk)

        return context

    def get_queryset(self):
        """
        Only show the Criterium objects connected to the specified experiment
        """
        return self.model.objects.filter(experiments=self.kwargs['experiment'])


class AddExistingCriteriumToExperimentView(braces.LoginRequiredMixin,
                                           RedirectSuccessMessageMixin,
                                           generic.RedirectView):
    success_message = _('criteria:messages:added_to_experiment')

    def get_redirect_url(self, *args, **kwargs):
        experiment_pk = self.kwargs.get('experiment')
        # Get the criterium from POST. No idea why it's a list, but it is...
        criterium_pk = self.request.POST.get('criterium')[0]

        criterium = Criterium.objects.get(pk=criterium_pk)
        criterium.experiments.add(experiment_pk)
        criterium.save()

        return reverse('experiments:specific_criteria', args=[experiment_pk])


class RemoveCriteriumFromExperiment(braces.LoginRequiredMixin,
                                    RedirectSuccessMessageMixin,
                                    generic.RedirectView):
    success_message = _('criteria:messages:removed_from_experiment')

    def get_redirect_url(self, *args, **kwargs):
        experiment_pk = self.kwargs.get('experiment')
        criterium_pk = self.kwargs.get('criterium')

        criterium = Criterium.objects.get(pk=criterium_pk)
        criterium.experiments.remove(experiment_pk)
        criterium.save()

        return reverse('experiments:specific_criteria', args=[experiment_pk])
