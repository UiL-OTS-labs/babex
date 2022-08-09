import braces.views as braces
from django import forms
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy as reverse
from django.utils.functional import cached_property
from django.utils.text import gettext_lazy as _
from django.views import generic
from cdh.core.views import FormSetUpdateView
from cdh.core.views.mixins import DeleteSuccessMessageMixin

from .forms import CriterionAnswerForm, ParticipantForm
from .models import CriterionAnswer, Participant, SecondaryEmail

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


class ParticipantUpdateView(braces.LoginRequiredMixin,
                            SuccessMessageMixin,
                            generic.UpdateView):
    model = Participant
    template_name = 'participants/edit.html'
    success_message = _('participants:messages:updated_participant')
    form_class = ParticipantForm
    secondary_email_formset = forms.inlineformset_factory(
        Participant,
        SecondaryEmail,
        fields=('email',),
        can_delete=True,
        extra=4
    )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['secondary_email_formset'] = kwargs.get(
            'secondary_email_formset',
            self.secondary_email_formset(instance=self.get_object())
        )

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        formset = self.secondary_email_formset(request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        elif not form.is_valid():
            return self.form_invalid(form)

        return self.render_to_response(
            self.get_context_data(
                form=form,
                secondary_email_formset=formset
            )
        )

    def form_valid(self, form, formset):
        message = "Admin updated participant '{}'".format(self.object)
        auditlog.log(
            Event.MODIFY_DATA,
            message,
            self.request.user,
            UserType.ADMIN
        )
        formset.save()
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
