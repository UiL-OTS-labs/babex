import braces.views as braces
from django.core.exceptions import SuspiciousOperation
from django.urls import reverse_lazy as reverse
from django.utils.functional import cached_property
from django.utils.text import gettext_lazy as _
from uil.core.views import RedirectActionView
from uil.core.views.mixins import RedirectSuccessMessageMixin

from experiments.utils.timeslot_create import add_timeslot
from main.views import ModelFormListView
from .mixins import ExperimentObjectMixin
from ..forms import TimeSlotForm
from ..models import TimeSlot
from ..utils import delete_timeslot, delete_timeslots, now, \
    unsubscribe_participant


class TimeSlotHomeView(braces.LoginRequiredMixin,
                       ExperimentObjectMixin, ModelFormListView):
    template_name = 'timeslots/index.html'
    model = TimeSlot
    form_class = TimeSlotForm

    def post(self, request, *args, **kwargs):
        """This override ensures that we don't redirect after a successfull
        form POST. This is because we actually want to stay on the page and
        have access to the POST values.

        These post values are needed to fill in the datetime initial value.
        (People like it when the last filled in value is already filled in)
        """
        form = self.get_form()
        if form.is_valid():
            self.form_valid(form)
            return self.get(request, *args, **kwargs)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """Only save the form, but stop there."""
        self.object = add_timeslot(
            self.experiment,
            form.cleaned_data['datetime'],
            form.cleaned_data['max_places']
        )

    def get_initial(self):
        initial = super(TimeSlotHomeView, self).get_initial()

        initial['max_places'] = self.experiment.default_max_places
        initial['datetime'] = self._get_datetime_initial()
        initial['experiment'] = self.experiment

        return initial

    def _get_datetime_initial(self):
        """If we have post values, we return the datetime from POST,
        otherwise we default to now().
        """
        if self.request.POST:
            return self.request.POST['datetime']

        return str(now())[:-3]  # Remove the seconds

    def get_queryset(self):
        # Only select them for this experiment
        qs = self.model.objects.filter(
            experiment=self.experiment,
        )

        # Force load all needed releated objects
        qs = qs.select_related('experiment')
        qs = qs.prefetch_related('appointments', 'appointments__participant')

        return qs

    def get_context_data(self, *_, **kwargs):
        context = super(TimeSlotHomeView, self).get_context_data(**kwargs)

        context['experiment'] = self.experiment

        return context


class TimeSlotDeleteView(braces.LoginRequiredMixin,
                         RedirectSuccessMessageMixin, ExperimentObjectMixin,
                         RedirectActionView):
    success_message = _('timeslots:message:deleted_timeslot')

    def action(self, request):
        timeslot_pk = self.kwargs.get('timeslot')

        delete_timeslot(
            self.experiment,
            timeslot_pk,
            deleting_user=request.user
        )

    def get_redirect_url(self, *args, **kwargs):
        return reverse('experiments:timeslots', args=[self.experiment.pk])


class TimeSlotBulkDeleteView(braces.LoginRequiredMixin,
                             RedirectSuccessMessageMixin, ExperimentObjectMixin,
                             RedirectActionView):
    success_message = _('timeslots:message:deleted_timeslots')

    def action(self, request):
        if not request.method == 'POST':
            raise SuspiciousOperation

        delete_timeslots(self.experiment, request.POST, request.user)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('experiments:timeslots', args=[self.experiment.pk])


class UnsubscribeParticipantView(braces.LoginRequiredMixin,
                                 RedirectSuccessMessageMixin,
                                 RedirectActionView):
    success_message = _('timeslots:message:unsubscribed_participant')

    def action(self, request):
        appointment_pk = self.kwargs.get('appointment')

        unsubscribe_participant(appointment_pk, deleting_user=request.user)

    def get_redirect_url(self, *args, **kwargs):
        if self.request.GET.get('next'):
            return self.request.GET.get('next')

        return reverse(
            'experiments:timeslots',
            args=[self.time_slot.experiment.pk]
        )

    @cached_property
    def time_slot(self):
        return TimeSlot.objects.get(pk=self.kwargs.get('time_slot'))


class SilentUnsubscribeParticipantView(UnsubscribeParticipantView):

    def action(self, request):
        appointment_pk = self.kwargs.get('appointment')

        unsubscribe_participant(appointment_pk,
                                False,
                                deleting_user=request.user)
