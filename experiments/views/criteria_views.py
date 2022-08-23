import braces.views as braces
from django.contrib.auth.views import SuccessURLAllowedHostsMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.http import Http404
from django.urls import reverse_lazy as reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views import generic
from cdh.core.views import RedirectActionView
from cdh.core.views.mixins import DeleteSuccessMessageMixin, \
    RedirectSuccessMessageMixin

from main.views import FormListView
from .mixins import ExperimentObjectMixin
from ..forms import CriterionForm, DefaultCriteriaForm, ExperimentCriterionForm
from ..models import Criterion, DefaultCriteria, ExperimentCriterion
from ..utils import attach_criterion, clean_form_existing_criterion, \
    create_and_attach_criterion


#
# Criteria views
#

class CriteriaHomeView(braces.LoginRequiredMixin, generic.ListView):
    model = Criterion
    template_name = 'criteria/index.html'

    def get_queryset(self):
        qs = self.model.objects.annotate(
            n_experiments=Count('experimentcriterion')
        )
        return qs


class CriteriaCreateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                         generic.CreateView):
    form_class = CriterionForm
    template_name = 'criteria/new.html'
    success_url = reverse('experiments:criteria_home')
    success_message = _('criteria:messages:created')


class CriteriaUpdateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                         generic.UpdateView):
    form_class = CriterionForm
    template_name = 'criteria/edit.html'
    success_url = reverse('experiments:criteria_home')
    success_message = _('criteria:messages:updated')
    model = Criterion


class CriteriaDeleteView(braces.LoginRequiredMixin,
                         DeleteSuccessMessageMixin, generic.DeleteView):
    success_message = _('criteria:messages:deleted')
    success_url = reverse('experiments:criteria_home')
    model = Criterion
    template_name = 'criteria/delete.html'

#
# Experiment Criteria views
#


class DefaultCriteriaUpdateView(
    braces.LoginRequiredMixin,
    SuccessURLAllowedHostsMixin,
    generic.UpdateView
):
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
        url = reverse('experiments:home')
        redirect_to = self.request.GET.get('next', url)

        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''


class CriteriaListView(braces.LoginRequiredMixin,
                       SuccessURLAllowedHostsMixin,
                       SuccessMessageMixin,
                       ExperimentObjectMixin,
                       FormListView):
    """
    This view is a bit special, it's both a ListView and a CreateView in one!
    In addition, there is a second form in the template that POSTs to the
    AddExistingCriterionToExperimentView view (below).

    The form_valid, get_initial and get_success_url are for the CreateView,
    the get_queryset is for the ListView and get_context_data is used for the
    second manual form.
    """
    template_name = 'criteria/specific_list.html'
    model = ExperimentCriterion
    form_class = ExperimentCriterionForm
    success_message = _('criteria:messages:created_and_added')

    def get_initial(self):
        """This makes sure that the add_criteria also adds it to the
        experiment, by adding the experiment to the hidden experiments field.
        """
        initial = super(CriteriaListView, self).get_initial()

        initial['experiments'] = [self.experiment]

        return initial

    def form_valid(self, form):
        """Intercept the form_valid method in order to create the objects
        as specified in the form.

        Returns the super() of this method to preserve functionality.
        """
        data = form.cleaned_data
        create_and_attach_criterion(
            self.experiment,
            data['name_form'],
            data['name_natural'],
            data['values'],
            data['correct_value'],
            data['message_failed'],
        )

        return super(CriteriaListView, self).form_valid(form)

    def get_success_url(self):
        url = reverse(
            'experiments:specific_criteria',
            args=[self.experiment.pk]
        )
        redirect_to = self.request.GET.get('next', url)

        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''

    def get_context_data(self, **kwargs):
        context = super(CriteriaListView, self).get_context_data(**kwargs)

        context['criteria_options'] = Criterion.objects.exclude(
            experimentcriterion__in=self.get_queryset()
        )

        context['experiment'] = self.experiment

        return context

    def get_queryset(self):
        """
        Only show the criterion objects connected to the specified experiment
        """
        return self.model.objects.filter(experiment_id=self.experiment.pk)


class AddExistingCriterionToExperimentView(braces.LoginRequiredMixin,
                                           RedirectSuccessMessageMixin,
                                           ExperimentObjectMixin,
                                           RedirectActionView):
    success_message = _('criteria:messages:added_to_experiment')

    def action(self, request):
        cleaned_data = clean_form_existing_criterion(request.POST)

        attach_criterion(
            self.experiment,
            cleaned_data['criterion'],
            cleaned_data['correct_value'],
            cleaned_data['message_failed'],
        )

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            'experiments:specific_criteria',
            args=[self.experiment.pk]
        )


class RemoveCriterionFromExperiment(braces.LoginRequiredMixin,
                                    RedirectSuccessMessageMixin,
                                    ExperimentObjectMixin,
                                    RedirectActionView):
    success_message = _('criteria:messages:removed_from_experiment')

    def action(self, request):
        criterion_pk = self.kwargs.get('criterion')

        ExperimentCriterion.objects.get(pk=criterion_pk).delete()

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            'experiments:specific_criteria',
            args=[self.experiment.pk]
        )
