import datetime
import json

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

from .forms import ExtraDataForm, ParticipantForm, LeaderParticipantForm
from .models import ExtraData, Participant, ParticipantData
from .permissions import can_leader_access_participant, participants_visible_to_leader


class ParticipantsHomeView(RandomLeaderMixin, generic.TemplateView):
    template_name = "participants/index.html"


class ParticipantListDataView(views.APIView):
    permission_classes = [IsRandomLeader]

    def get_queryset(self):
        if self.request.user.is_staff:
            return (
                Participant.objects.filter(deactivated=None).select_related("data").prefetch_related("data__languages")
            )
        return participants_visible_to_leader(self.request.user)

    def format_row(self, pp: Participant):
        pp_url = reverse("participants:detail", args=(pp.pk,))

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
        order_by = int(request.GET.get("order[0][column]", 0))
        order_asc = request.GET.get("order[0][dir]") in [None, "asc"]
        search = request.GET.get("search[value]")

        columns = ["name", "birth_date", "age", "sex", "phonenumber", "multilingual", "created"]
        qs = self.get_queryset()
        total = qs.count()
        filtered = qs
        if search is not None:
            search = search.lower()
            filtered = [row for row in qs if search in row.name.lower() or search in row.phonenumber]
        as_list = sorted(filtered, key=lambda row: getattr(row, columns[order_by]), reverse=not order_asc)
        pps = [self.format_row(pp) for pp in as_list[start : start + length]]
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

    def get_form_class(self):
        if self.request.user.is_staff:
            return ParticipantForm
        return LeaderParticipantForm

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
        criteria = json.loads(request.GET.get("criteria", "{}"))
        participants = (
            Participant.objects.filter(deactivated=None).select_related("data").prefetch_related("data__languages")
        )
        date = datetime.date.today()
        if "date" in request.GET:
            date = datetime.datetime.strptime(request.GET["date"], "%Y-%m-%d").date()

        if "experiment" in request.GET:
            participants = get_eligible_participants_for_experiment(
                Experiment.objects.get(pk=request.GET["experiment"])
            )
            result = set(participants)

        def age(pp):
            return date_of_birth(pp.birth_date).on(date).age_ym()

        if "experiment" not in request.GET:
            # only apply criteria if not looking at a specific experiment

            dyslexia_result = set()
            if criteria.get("dyslexia_yes"):
                dyslexia_result.update(
                    [pp for pp in participants if pp.dyslexic_parent not in (None, Participant.WhichParent.NEITHER)]
                )
            if criteria.get("dyslexia_no"):
                dyslexia_result.update(
                    [pp for pp in participants if pp.dyslexic_parent in (None, Participant.WhichParent.NEITHER)],
                )

            multilingual_result = set()
            if criteria.get("multilingual_yes"):
                multilingual_result.update([pp for pp in participants if pp.multilingual])
            if criteria.get("multilingual_no"):
                multilingual_result.update([pp for pp in participants if not pp.multilingual])

            premature_result = set()
            if criteria.get("premature_yes"):
                premature_result.update(
                    [pp for pp in participants if pp.pregnancy_duration == Participant.PregnancyDuration.LESS_THAN_37]
                )
            if criteria.get("premature_no"):
                premature_result.update(
                    [pp for pp in participants if pp.pregnancy_duration != Participant.PregnancyDuration.LESS_THAN_37]
                )

            result = dyslexia_result.intersection(multilingual_result).intersection(premature_result)
        ages = [age(pp) for pp in result]
        return JsonResponse(dict(all=ages))


class ExtraDataAddView(RandomLeaderMixin, SuccessMessageMixin, generic.CreateView):
    model = ExtraData
    form_class = ExtraDataForm

    def form_valid(self, form):
        form.instance.participant = Participant.objects.get(pk=self.kwargs["pk"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("participants:detail", args=(self.object.participant.pk,))
