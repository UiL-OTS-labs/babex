from cdh.core.views.mixins import DeleteSuccessMessageMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy as reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from comments.forms import CommentForm
from main.auth.util import LabManagerMixin, RandomLeaderMixin
from participants.permissions import (
    can_leader_access_participant,
    participants_visible_to_leader,
)

from . import graphs
from .forms import ExtraDataForm, ParticipantForm
from .models import ExtraData, Participant, ParticipantData


class ParticipantsHomeView(RandomLeaderMixin, generic.ListView):
    template_name = "participants/index.html"
    model = Participant

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.model.objects.filter(deactivated=None)

        return participants_visible_to_leader(self.request.user)


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


def render_demograhpics(request: HttpRequest, kind: str, width: int = 850, height: int = 0):
    """Renders the histograms for the
    render_demograhpics_png and render_demograhpics_svg views
    """

    if not height:
        height = (width * 9) // 16

    if kind == "histo":
        img_bytes = graphs.render_demograhpics(width, height)
    elif kind == "histo_grouped":
        img_bytes = graphs.render_demograhpics_by_group(width, height)
    content_type = "image/svg+xml"
    return HttpResponse(img_bytes, content_type=content_type)


class ExtraDataAddView(RandomLeaderMixin, SuccessMessageMixin, generic.CreateView):
    model = ExtraData
    form_class = ExtraDataForm

    def form_valid(self, form):
        form.instance.participant = Participant.objects.get(pk=self.kwargs["pk"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("participants:detail", args=(self.object.participant.pk,))
