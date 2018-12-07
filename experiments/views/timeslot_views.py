from django.urls import reverse_lazy as reverse
from django.core.exceptions import SuspiciousOperation
from django.utils.functional import cached_property
from django.utils.text import gettext_lazy as _
from django.views import generic
import braces.views as braces

from ..models import TimeSlot
from ..forms import TimeSlotForm
from .mixins import ExperimentObjectMixin
from ..utils import now, delete_timeslot, delete_timeslots, \
    unsubscribe_participant
from main.views import FormListView
from uil.core.views.mixins import RedirectSuccessMessageMixin


class TimeSlotHomeView(braces.LoginRequiredMixin,
                       ExperimentObjectMixin, FormListView):
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
        self.object = form.save()

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
        return self.model.objects.filter(experiment=self.experiment)

    def get_context_data(self, *_, **kwargs):
        context = super(TimeSlotHomeView, self).get_context_data(**kwargs)

        context['experiment'] = self.experiment

        return context


class TimeSlotDeleteView(braces.LoginRequiredMixin,
                         RedirectSuccessMessageMixin, ExperimentObjectMixin,
                         generic.RedirectView):
    success_message = _('timeslots:message:deleted_timeslot')

    def get_redirect_url(self, *args, **kwargs):
        timeslot_pk = self.kwargs.get('timeslot')

        delete_timeslot(self.experiment, timeslot_pk)

        return reverse('experiments:timeslots', args=[self.experiment.pk])


class TimeSlotBulkDeleteView(braces.LoginRequiredMixin,
                             RedirectSuccessMessageMixin, ExperimentObjectMixin,
                             generic.RedirectView):
    success_message = _('timeslots:message:deleted_timeslots')

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.method == 'POST':
            raise SuspiciousOperation

        delete_timeslots(self.experiment, self.request.POST)

        return reverse('experiments:timeslots', args=[self.experiment.pk])


class UnsubscribeParticipantView(braces.LoginRequiredMixin,
                                 RedirectSuccessMessageMixin,
                                 generic.RedirectView):
    success_message = _('timeslots:message:unsubscribed_participant')

    def get_redirect_url(self, *args, **kwargs):
        participant_pk = self.kwargs.get('participant')

        unsubscribe_participant(self.time_slot, participant_pk)

        return reverse(
            'experiments:timeslots',
            args=[self.time_slot.experiment.pk]
        )

    @cached_property
    def time_slot(self):
        return TimeSlot.objects.get(pk=self.kwargs.get('time_slot'))


class SilentUnsubscribeParticipantView(braces.LoginRequiredMixin,
                                       RedirectSuccessMessageMixin,
                                       generic.RedirectView):
    success_message = _('timeslots:message:unsubscribed_participant')

    def get_redirect_url(self, *args, **kwargs):
        participant_pk = self.kwargs.get('participant')

        unsubscribe_participant(self.time_slot, participant_pk, False)

        return reverse(
            'experiments:timeslots',
            args=[self.time_slot.experiment.pk]
        )

    @cached_property
    def time_slot(self):
        return TimeSlot.objects.get(pk=self.kwargs.get('time_slot'))
