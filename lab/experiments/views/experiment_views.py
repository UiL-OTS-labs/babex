import braces.views as braces
from cdh.core.views.mixins import DeleteSuccessMessageMixin
from django.contrib.auth.views import RedirectURLMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.http.response import HttpResponse
from django.urls import reverse_lazy as reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views import View, generic

from main.auth.util import ExperimentLeaderMixin, LabManagerMixin, RandomLeaderMixin

from ..forms import ExperimentForm
from ..models import Appointment, Experiment
from .mixins import ExperimentObjectMixin

# --------------------------------------
# List, create, detail, update and delete views
# --------------------------------------


class ExperimentHomeView(RandomLeaderMixin, generic.ListView):
    template_name = "experiments/index.html"
    model = Experiment

    def get_queryset(self):
        qs = self.model.objects.select_related("location")

        if not self.request.user.is_staff:
            qs = qs.filter(pk__in=self.request.user.experiments.all())

        count_participants = Count("timeslot__appointments", distinct=True)
        count_excluded_experiments = Count("excluded_experiments", distinct=True)

        return qs.annotate(
            n_participants=count_participants,
            n_excluded_experiments=count_excluded_experiments,
        )


class ExperimentCreateView(LabManagerMixin, SuccessMessageMixin, generic.CreateView):
    template_name = "experiments/new.html"
    form_class = ExperimentForm
    success_message = _("experiments:message:create:success")

    # need to pass the CSP nonce from the view to form widgets
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["csp_nonce"] = str(self.request.csp_nonce) if hasattr(self.request, "csp_nonce") else ""
        return kwargs

    def get_success_url(self):
        return reverse("experiments:default_criteria", args=[self.object.pk])


class ExperimentUpdateView(LabManagerMixin, RedirectURLMixin, SuccessMessageMixin, generic.UpdateView):
    template_name = "experiments/edit.html"
    form_class = ExperimentForm
    model = Experiment
    success_message = _("experiments:message:update:success")

    # need to pass the CSP nonce from the view to form widgets
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["csp_nonce"] = str(self.request.csp_nonce) if hasattr(self.request, "csp_nonce") else ""
        return kwargs

    def get_success_url(self):
        url = reverse("experiments:home")
        redirect_to = self.request.GET.get("next", url)

        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ""


class ExperimentDetailView(ExperimentLeaderMixin, ExperimentObjectMixin, generic.DetailView):
    template_name = "experiments/detail.html"
    model = Experiment
    experiment_kwargs_name = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["appointments"] = self.object.appointments.all()

        # progress overview
        progress = dict(
            target=self.object.recruitment_target,
            tested=self.object.appointments.filter(outcome=Appointment.Outcome.COMPLETED).count(),
            # TODO: is it better to check the date of the appointment?
            planned=self.object.appointments.filter(outcome=None).count(),
            excluded=self.object.appointments.filter(outcome=Appointment.Outcome.EXCLUDED).count(),
        )
        progress["to_plan"] = max(0, progress["target"] - progress["tested"] - progress["planned"])
        progress["to_test"] = max(0, progress["target"] - progress["tested"])
        context["progress"] = progress
        return context


class ExperimentDeleteView(braces.SuperuserRequiredMixin, DeleteSuccessMessageMixin, generic.DeleteView):
    model = Experiment
    success_url = reverse("experiments:home")
    template_name = "experiments/delete.html"
    success_message = _("experiments:message:deleted_experiment")


class ExperimentAppointmentsView(ExperimentLeaderMixin, ExperimentObjectMixin, generic.TemplateView):
    template_name = "experiments/participants.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context["experiment"] = self.experiment
        queryset = (
            Appointment.objects.filter(experiment=self.experiment)
            .exclude(outcome=Appointment.Outcome.CANCELED)
            .exclude(outcome=Appointment.Outcome.NOSHOW)
        )
        context["past_list"] = queryset.filter(timeslot__start__lt=timezone.now())
        context["future_list"] = queryset.filter(timeslot__start__gte=timezone.now())
        context["excluded_list"] = queryset.filter(outcome=Appointment.Outcome.EXCLUDED)
        return context


class ExperimentAttachmentView(ExperimentLeaderMixin, ExperimentObjectMixin, View):
    experiment_kwargs_name = "pk"

    def get(self, request, *args, **kwargs):
        attachment = self.experiment.attachments.get(pk=kwargs["attachment"])
        response = HttpResponse(attachment.file, content_type=attachment.file.content_type)
        response["Content-Disposition"] = "attachment; filename=" + attachment.filename
        return response


class ExperimentCriteriaView(LabManagerMixin, ExperimentObjectMixin, generic.TemplateView):
    """used to display an html table with filter criteria on the demographics view"""

    experiment_kwargs_name = "pk"
    template_name = "experiments/criteria_snippet.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["experiment"] = self.experiment
        return context
