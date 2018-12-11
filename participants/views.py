from django.views import generic
from django.utils.functional import cached_property
from django.utils.text import gettext_lazy as _
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy as reverse
import braces.views as braces

from .models import Participant, CriteriumAnswer
from .forms import ParticipantForm, CriteriumAnswerForm
from uil.core.views.base import FormSetUpdateView


class ParticipantsHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'participants/index.html'
    model = Participant


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


class ParticipantSpecificCriteriaUpdateView(braces.LoginRequiredMixin,
                                            SuccessMessageMixin,
                                            FormSetUpdateView):
    """"""
    form = CriteriumAnswerForm
    template_name = 'participants/specific_criteria.html'

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
