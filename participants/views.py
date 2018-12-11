from django.views import generic
from django.utils.text import gettext_lazy as _
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy as reverse
import braces.views as braces

from .models import Participant
from .forms import ParticipantForm


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
