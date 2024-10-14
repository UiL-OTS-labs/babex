import datetime

from ageutil import date_of_birth
from cdh.core.views.mixins import DeleteSuccessMessageMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy as reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic
from rest_framework import views

from comments.forms import CommentForm
from experiments.models import Experiment
from experiments.utils.exclusion import get_eligible_participants_for_experiment
from main.auth.util import (
    IsLabManager,
    IsRandomLeader,
    LabManagerMixin,
    RandomLeaderMixin,
)

from .forms import ExtraDataForm, ParticipantForm
from .models import ExtraData, Participant, ParticipantData
from .permissions import can_leader_access_participant, participants_visible_to_leader


class ParticipantsHomeView(RandomLeaderMixin, generic.ListView):
    template_name = "participants/index.html"
    model = Participant

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.model.objects.filter(deactivated=None)

        return participants_visible_to_leader(self.request.user)


class ParticipantListDataView(views.APIView):
    permission_classes = [IsRandomLeader]

    def get_queryset(self):
        if self.request.user.is_staff:
            q = Participant.objects.filter(deactivated=None)
        else:
            q = participants_visible_to_leader(self.request.user)

        return q.select_related("data").prefetch_related("data__languages")

    def format_row(self, pp: Participant):
        pp_url = "#"

        return [
            f'<a href="{pp_url}">{pp.fullname}</a>',
            pp.birth_date.strftime("%Y-%m-%d"),
            pp.age,
            pp.get_sex_display() or "",
            pp.phonenumber,
            _("options:yes,empty").split(",")[pp.multilingual],
            pp.created.strftime("%Y-%m-%d"),
            render_to_string("participants/actions.html", dict(participant=pp), request=self.request),
        ]

    def get(self, request, *args, **kwargs):
        start = int(request.GET["start"])
        length = int(request.GET["length"])
        qs = self.get_queryset()
        total = qs.count()
        pps = [self.format_row(pp) for pp in qs[start : start + length]]
        return JsonResponse(dict(draw=int(request.GET["draw"]), recordsTotal=total, recordsFiltered=total, data=pps))


class ParticipantDetailView(RandomLeaderMixin, generic.DetailView):
    model = Participant
    template_name = "participants/detail.html"

    def test_leader(self, user):
        return can_leader_access_participant(user, self.get_object())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["comment_form"] = CommentForm(initial=dict(participant=self.get_object()))
        return context


class ParticipantUpdateView(RandomLeaderMixin, SuccessMessageMixin, generic.UpdateView):
    model = ParticipantData
    template_name = "participants/edit.html"
    success_message = _("participants:messages:updated_participant")
    form_class = ParticipantForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_success_url(self):
        return reverse("participants:detail", args=[self.object.pk])

    def test_leader(self, user):
        return can_leader_access_participant(user, self.get_object())


class ParticipantDeleteView(LabManagerMixin, DeleteSuccessMessageMixin, generic.DeleteView):
    success_url = reverse("participants:home")
    success_message = _("participants:messages:deleted_participant")
    template_name = "participants/delete.html"
    model = Participant

    def post(self, request, *args, **kwargs):
        if "deactivate" in self.request.POST:
            self.get_object().deactivate()
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)


class ParticipantsDemographicsView(LabManagerMixin, generic.TemplateView):
    template_name = "participants/demographics.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context.update(
            dict(
                experiments={
                    e.pk: dict(
                        pk=e.pk,
                        name=e.name,
                        min_months=e.defaultcriteria.min_age_months,
                        max_months=e.defaultcriteria.max_age_months,
                    )
                    for e in Experiment.objects.all()
                }
            )
        )
        return context


class DemographicsDataView(views.APIView):
    permission_classes = [IsLabManager]

    def get(self, request):
        participants = Participant.objects.filter(deactivated=None)
        date = datetime.date.today()
        if "date" in request.GET:
            date = datetime.datetime.strptime(request.GET["date"], "%Y-%m-%d").date()

        if "experiment" in request.GET:
            participants = get_eligible_participants_for_experiment(
                Experiment.objects.get(pk=request.GET["experiment"])
            )

        def age(pp):
            return date_of_birth(pp.birth_date).on(date).age_ym()

        all = [age(pp) for pp in participants]
        dyslexia = {
            "Yes": [
                age(pp) for pp in participants if pp.dyslexic_parent not in (None, Participant.WhichParent.NEITHER)
            ],
            "No": [age(pp) for pp in participants if pp.dyslexic_parent in (None, Participant.WhichParent.NEITHER)],
        }
        multilingual = {
            "Yes": [age(pp) for pp in participants if pp.multilingual],
            "No": [age(pp) for pp in participants if not pp.multilingual],
        }

        premature = {
            "Yes": [
                age(pp) for pp in participants if pp.pregnancy_duration == Participant.PregnancyDuration.LESS_THAN_37
            ],
            "No": [
                age(pp) for pp in participants if pp.pregnancy_duration != Participant.PregnancyDuration.LESS_THAN_37
            ],
        }

        return JsonResponse(dict(all=all, dyslexia=dyslexia, multilingual=multilingual, premature=premature))


class ExtraDataAddView(RandomLeaderMixin, SuccessMessageMixin, generic.CreateView):
    model = ExtraData
    form_class = ExtraDataForm

    def form_valid(self, form):
        form.instance.participant = Participant.objects.get(pk=self.kwargs["pk"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("participants:detail", args=(self.object.participant.pk,))
