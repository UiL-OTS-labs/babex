from django.views import generic
from django.utils.functional import cached_property
from django.utils.text import gettext_lazy as _
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy as reverse
import braces.views as braces

from .models import Participant, CriteriumAnswer
from .forms import ParticipantForm, CriteriumAnswerForm, ParticipantMergeForm
from .utils import merge_participants
from uil.core.views import FormSetUpdateView
from uil.core.views.mixins import DeleteSuccessMessageMixin


class ParticipantsHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'participants/index.html'
    model = Participant

    def get_queryset(self):
        return self.model.objects.prefetch_related('secondaryemail_set')


class ParticipantDetailView(braces.LoginRequiredMixin, generic.DetailView):
    model = Participant
    template_name = 'participants/detail.html'


class ParticipantUpdateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                            generic.UpdateView):
    model = Participant
    template_name = 'participants/edit.html'
    success_message = _('participants:messages:updated_participant')
    form_class = ParticipantForm

    def get_success_url(self):
        return reverse('participants:detail', args=[self.object.pk])


class ParticipantDeleteView(braces.LoginRequiredMixin,
                            DeleteSuccessMessageMixin, generic.DeleteView):
    success_url = reverse('participants:home')
    success_message = _('participants:messages:deleted_participant')
    template_name = 'participants/delete.html'
    model = Participant


class ParticipantSpecificCriteriaUpdateView(braces.LoginRequiredMixin,
                                            FormSetUpdateView):
    form = CriteriumAnswerForm
    template_name = 'participants/specific_criteria.html'
    succes_url = reverse('participants:home')

    def get_queryset(self):

        return CriteriumAnswer.objects.filter(participant=self.participant)

    def get_context_data(self, **kwargs):
        context = super(ParticipantSpecificCriteriaUpdateView,
                        self).get_context_data(**kwargs)

        context['participant'] = self.participant

        return context

    @cached_property
    def participant(self):
        participant_pk = self.kwargs.get('pk')

        return Participant.objects.get(pk=participant_pk)


class ParticipantMergeView(braces.LoginRequiredMixin, SuccessMessageMixin,
                           generic.FormView):
    success_url = reverse('participants:home')
    success_message = _('participants:messages:merged_participants')
    template_name = 'participants/merge.html'
    form_class = ParticipantMergeForm

    def form_valid(self, form):
        data = form.cleaned_data

        merge_participants(data['old_participant'], data['new_participant'])

        return super(ParticipantMergeView, self).form_valid(form)
