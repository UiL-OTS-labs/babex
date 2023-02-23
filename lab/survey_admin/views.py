from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView

from .models import SurveyDefinition


class SurveyOverview(ListView):
    # TODO: permissions
    queryset = SurveyDefinition.objects.all()
    template_name = 'survey_admin/index.html'


class SurveyPreview(DetailView):
    # TODO: permissions
    queryset = SurveyDefinition.objects.all()
    template_name = 'survey_admin/preview.html'


def overview(request):
    return HttpResponse('')
