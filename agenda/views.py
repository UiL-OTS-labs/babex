import dateutil.parser

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django import forms
from django.shortcuts import render
from django.urls import reverse_lazy as reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from rest_framework import generics

from experiments.models import Appointment, Experiment, Location, TimeSlot
from experiments.models.appointment_models import AppointmentSerializer
from .models import Closing, ClosingSerializer


class AppointmentFeed(generics.ListAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        from_date = dateutil.parser.isoparse(self.request.GET['start'])
        to_date = dateutil.parser.isoparse(self.request.GET['end'])
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

    if request.headers.get('HX-Request'):
        return render(request, 'agenda/calendar_fragment.html', context)
    else:
        return render(request, 'agenda/home.html', context)


class ClosingFeed(generics.ListAPIView):
    serializer_class = ClosingSerializer

    def get_queryset(self):
        from_date = dateutil.parser.isoparse(self.request.GET['start'])
        to_date = dateutil.parser.isoparse(self.request.GET['end'])
        return Closing.objects.filter(end__gte=from_date, start__lt=to_date)


class ClosingForm(forms.ModelForm):
    class Meta:
        model = Closing
        fields = ['start', 'end', 'location', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start'].widget.format = '%Y-%m-%d %H:%M'
        self.fields['end'].widget.format = '%Y-%m-%d %H:%M'
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
        if self.request.method == 'GET':
            start = timezone.localtime(dateutil.parser.isoparse(self.request.GET.get('start')))
            end = timezone.localtime(dateutil.parser.isoparse(self.request.GET.get('end')))
            kwargs['initial']['start'] = start.strftime('%Y-%m-%d %H:%M')
            kwargs['initial']['end'] = end.strftime('%Y-%m-%d %H:%M')
        return kwargs


class ClosingEditView(UpdateView):
    model = Closing
    form_class = ClosingForm
    success_url = reverse('agenda:success')


class ClosingDeleteView(DeleteView):
    model = Closing
    success_url = reverse('agenda:success')


def agenda_success(request):
    return HttpResponse('', headers={'HX-Trigger': 'agendaRefresh'})


class AppointmentAddView(CreateView):
    def get(self, request, experiment):
        experiment = Experiment.objects.get(pk=experiment)
        return render(request, 'agenda/calendar_modal.html', dict(experiment=experiment))

    # only adding a timeslot for now as a lazy placeholder for real
    # appointment management
    def post(self, request, experiment):
        experiment = Experiment.objects.get(pk=experiment)
        experiment = Experiment.objects.first()
        TimeSlot.objects.create(
            experiment=experiment,
            datetime=request.POST['start'],
            max_places=1)
        success_url = reverse('experiments:timeslots', args=[experiment.pk])
        return HttpResponse(status=204, headers={'HX-Redirect': success_url})
