import dateutil.parser

from django.contrib.auth.decorators import login_required
from django import forms
from django.http.response import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy as reverse
from django.utils.translation import gettext as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from rest_framework import generics

from experiments.models import Appointment, Location
from experiments.models.appointment_models import AppointmentSerializer
from .models import Closing, ClosingSerializer


class AppointmentFeed(generics.ListAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        from_date = dateutil.parser.parse(self.request.GET['start'])
        to_date = dateutil.parser.parse(self.request.GET['end'])
        return Appointment.objects.filter(timeslot__datetime__gte=from_date, timeslot__datetime__lt=to_date)


class AppointmentInfo(DetailView):
    model = Appointment
    template_name = 'agenda/appointment_info.html'


@login_required
def agenda_home(request):
    locations = Location.objects.all()

    def format_location(location):
        return dict(
            id=location.id,
            name=location.name)

    context = dict()
    context['locations'] = [format_location(x) for x in locations]

    return render(request, 'agenda/home.html', context)


class ClosingFeed(generics.ListAPIView):
    serializer_class = ClosingSerializer

    def get_queryset(self):
        from_date = dateutil.parser.parse(self.request.GET['start'])
        to_date = dateutil.parser.parse(self.request.GET['end'])
        return Closing.objects.filter(end__gte=from_date, start__lt=to_date)


class ClosingForm(forms.ModelForm):
    class Meta:
        model = Closing
        fields = ['start', 'end', 'location', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].required = False
        self.fields['location'].empty_label = _('Entire building')
        self.fields['comment'].required = False

    def save(self, *args, **kwargs):
        self.instance.is_global = self.instance.location is None
        return super().save(*args, **kwargs)


class ClosingAddView(CreateView):
    model = Closing
    form_class = ClosingForm
    success_url = reverse('agenda:success')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial']['start'] = self.request.GET.get('start')
        kwargs['initial']['end'] = self.request.GET.get('end')
        return kwargs


class ClosingEditView(UpdateView):
    model = Closing
    form_class = ClosingForm
    success_url = reverse('agenda:success')


class ClosingDeleteView(DeleteView):
    model = Closing
    success_url = reverse('agenda:success')


def agenda_success(request):
    return HttpResponse('OK', headers={'HX-Trigger': 'agendaRefresh'})
