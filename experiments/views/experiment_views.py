import braces.views as braces
from django.contrib import messages
from django.contrib.auth.views import SuccessURLAllowedHostsMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, F, Q
from django.urls import reverse_lazy as reverse
from django.utils.http import is_safe_url
from django.utils.translation import gettext_lazy as _
from django.views import generic
from uil.core.views import RedirectActionView
from uil.core.views.mixins import DeleteSuccessMessageMixin, \
    RedirectSuccessMessageMixin

from comments.models import Comment
from experiments.utils.remind_participant import remind_participant
from .mixins import ExperimentObjectMixin
from ..forms import ExperimentForm
from ..models import Appointment, Experiment

from django.core.exceptions import SuspiciousOperation


# --------------------------------------
# List, create, detail, update and delete views
# --------------------------------------

class ExperimentHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'experiments/index.html'
    model = Experiment

    def get_queryset(self):
        qs = self.model.objects.select_related('location')

        count_participants = Count('timeslot__appointments', distinct=True)
        count_excluded_experiments = Count('excluded_experiments',
                                           distinct=True)

        return qs.annotate(
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


class ExperimentUpdateView(braces.LoginRequiredMixin,
                           SuccessURLAllowedHostsMixin,
                           SuccessMessageMixin,
                           generic.UpdateView):
    template_name = 'experiments/edit.html'
    form_class = ExperimentForm
    model = Experiment
    success_message = _('experiments:message:update:success')

    def get_success_url(self):
        url = reverse('experiments:home')
        redirect_to = self.request.GET.get('next', url)

        url_is_safe = is_safe_url(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''


class ExperimentDetailView(braces.LoginRequiredMixin, generic.DetailView):
    template_name = 'experiments/detail.html'
    model = Experiment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['timeslots'] = self._get_timeslots()
        context['appointments'] = self.object.appointments.all()
        context['comments'] = Comment.objects.filter(experiment=self.object)

        return context

    def _get_timeslots(self):
        timeslots = self.object.timeslot_set.all()
        out = []

        for timeslot in timeslots:  # Type: TimeSlot
            out.append(
                (timeslot.datetime, timeslot.free_places,
                 timeslot.max_places - timeslot.free_places)
            )

        return out


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
        return Experiment.objects.exclude(
            pk=self.kwargs['experiment']
        ).select_related(
            'leader',
        ).prefetch_related(
            'additional_leaders',
        )

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


class ExperimentAppointmentsView(braces.LoginRequiredMixin,
                                 ExperimentObjectMixin, generic.ListView):
    template_name = 'experiments/participants.html'
    model = Appointment

    # Prefetch/select related criteria data for the criteria boxes
    experiment_select_related = ['defaultcriteria']
    experiment_prefetch_related = ['experimentcriterion_set__criterion']

    def get_context_data(self, *args, **kwargs):
        context = super(ExperimentAppointmentsView, self).get_context_data(
            *args,
            **kwargs
        )

        context['experiment'] = self.experiment

        return context

    def get_queryset(self):
        """
        Returns an annotated queryset, which injects the `n` attribute. This
        will hold the place this appointment has in a time slot.
        :return:
        """

        # First, get a QuerySet containing only appointments for this experiment
        qs = self.model.objects.filter(experiment=self.experiment)

        # Ensure the time slot and participant objects are collected in the
        # initial SELECT query
        qs = qs.select_related('timeslot', 'participant')

        # Build a query filter that selects all appointments with a lower or
        # equal creation date
        # (the equal part makes sure we count the appointment in question
        # too, which is a hack to ensure that we display a 1-based place)
        q_filter = None
        if self.experiment.use_timeslots:
            # If we use timeslots, we actually use the timeslot's set of
            # appointments, to ensure that the counter is for appointments in
            # that slot
            q_filter = Q(
                timeslot__appointments__creation_date__lte=F('creation_date')
            )
        else:
            # If we don't use timeslots, we can just count all appointments
            q_filter = Q(
                creation_date__lte=F('creation_date')
            )

        # Make an aggregation object that counts the number of appointments,
        # filtered by the filter we made above
        # This means this will count all appointments with a lower creation_date
        count = Count('timeslot__appointments', filter=q_filter)

        return qs.annotate(n=count)


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


class RemindParticipantsView(braces.LoginRequiredMixin,
                             ExperimentObjectMixin,
                             RedirectActionView):

    def action(self, request):
        if not request.POST:
            raise SuspiciousOperation

        if "reminder[]" in request.POST:
            reminders = request.POST.getlist('reminder[]')

            for reminder in reminders:
                appointment = Appointment.objects.get(pk=reminder)
                remind_participant(appointment)

            messages.success(self.request,
                             str(
                                 _('experiments:message:sent_reminders')
                                ).format(len(reminders))
                             )

    def get_redirect_url(self, *args, **kwargs):
        return reverse('experiments:participants', args=[self.experiment.pk])
