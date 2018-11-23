from django.views import generic
import braces.views as braces

from .models import Participant


class ParticipantsHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'participants/index.html'
    model = Participant
