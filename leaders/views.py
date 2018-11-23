from django.views import generic
import braces.views as braces

from .models import Leader


class LeaderHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'leaders/index.html'
    model = Leader
