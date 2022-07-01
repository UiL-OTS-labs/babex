import braces.views as braces

from django.shortcuts import render
from django.views.generic import TemplateView


class AgendaHomeView(braces.LoginRequiredMixin, TemplateView):
    template_name = 'agenda/home.html'
