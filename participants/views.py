from typing import Any
import braces.views as braces
from django import forms
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy as reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.http import HttpRequest, HttpResponse, Http404
from cdh.core.views import FormSetUpdateView
from cdh.core.views.mixins import DeleteSuccessMessageMixin

from .forms import CriterionAnswerForm, ParticipantForm
from .models import CriterionAnswer, Participant, SecondaryEmail
from comments.forms import CommentForm

from . import graphs

from auditlog.enums import Event, UserType
import auditlog.utils.log as auditlog


class ParticipantsHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'participants/index.html'
    model = Participant

    def get_queryset(self):
        return self.model.objects.prefetch_related('secondaryemail_set')


class ParticipantDetailView(braces.LoginRequiredMixin,
                            generic.DetailView):
    model = Participant
    template_name = 'participants/detail.html'

    def get(self, request, *args, **kwargs):
        message = "Admin viewed participant '{}'".format(self.get_object())
        auditlog.log(
            Event.VIEW_SENSITIVE_DATA,
            message,
            self.request.user,
            UserType.ADMIN
        )

        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['comment_form'] = CommentForm(initial=dict(participant=self.get_object()))
        return context


class ParticipantUpdateView(braces.LoginRequiredMixin,
                            SuccessMessageMixin,
                            generic.UpdateView):
    model = Participant
    template_name = 'participants/edit.html'
    success_message = _('participants:messages:updated_participant')
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

    def form_valid(self, form):
        message = "Admin updated participant '{}'".format(self.object)
        auditlog.log(
            Event.MODIFY_DATA,
            message,
            self.request.user,
            UserType.ADMIN
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('participants:detail', args=[self.object.pk])


class ParticipantDeleteView(braces.LoginRequiredMixin,
                            DeleteSuccessMessageMixin, generic.DeleteView):
    success_url = reverse('participants:home')
    success_message = _('participants:messages:deleted_participant')
    template_name = 'participants/delete.html'
    model = Participant

    def delete(self, request, *args, **kwargs):
        participant = self.get_object()

        message = "Admin deleted participant '{}'".format(participant)
        auditlog.log(
            Event.DELETE_DATA,
            message,
            self.request.user,
            UserType.ADMIN
        )

        participant.appointments.all().delete()

        return super().delete(request, *args, **kwargs)


class ParticipantSpecificCriteriaUpdateView(braces.LoginRequiredMixin,
                                            FormSetUpdateView):
    form = CriterionAnswerForm
    template_name = 'participants/specific_criteria.html'
    succes_url = reverse('participants:home')

    def get_queryset(self):
        return CriterionAnswer.objects.filter(participant=self.participant)

    def get_context_data(self, **kwargs):
        context = super(ParticipantSpecificCriteriaUpdateView,
                        self).get_context_data(**kwargs)

        context['participant'] = self.participant

        return context

    @cached_property
    def participant(self):
        participant_pk = self.kwargs.get('pk')

        return Participant.objects.get(pk=participant_pk)


class ParticipantsDemographicsView(generic.TemplateView,
                                   braces.LoginRequiredMixin):

    template_name = 'participants/demographics.html'


def render_demograhpics(
        request: HttpRequest,
        img_format: str = "png",
        width: int = 850,
        height: int = 0):
    """Renders the histograms for the
    render_demograhpics_png and render_demograhpics_svg views
    """

    supported_formats = ["png", "svg"]
    if img_format not in supported_formats:
        return Http404("Unsupported image format")

    if not height:
        height = (width * 9) // 16

    if img_format == "png":
        # Keep returned png small
        width = min(1920, width)
        height = min(1080, height)

    img_bytes = graphs.render_demograhpics(width, height, img_format)
    content_type = "image/"
    content_type += img_format if img_format == "png" else "svg+xml"

    return HttpResponse(img_bytes, content_type=content_type)


def render_demograhpics_png(
        request: HttpRequest,
        width: int = 850,
        height: int = 0):
    return render_demograhpics(request, "png", width, height)


def render_demograhpics_svg(
        request: HttpRequest,
        width: int = 850,
        height: int = 0):
    return render_demograhpics(request, "svg", width, height)
