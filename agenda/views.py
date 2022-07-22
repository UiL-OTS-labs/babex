from datetime import timedelta, datetime
import dateutil.parser

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http.response import JsonResponse

from rest_framework import generics, views, serializers, viewsets
from rest_framework.response import Response

from experiments.models import Appointment, Location
from experiments.models.appointment_models import AppointmentSerializer
from .models import Closing, ClosingSerializer


class AppointmentFeed(generics.ListAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        from_date = dateutil.parser.parse(self.request.GET['start'])
        to_date = dateutil.parser.parse(self.request.GET['end'])
        return Appointment.objects.filter(timeslot__datetime__gte=from_date, timeslot__datetime__lt=to_date)


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


class ClosingViewSet(viewsets.ModelViewSet):
    serializer_class = ClosingSerializer

    def get_queryset(self):
        queryset = Closing.objects.all()
        if self.request.method == 'GET':
            from_date = dateutil.parser.parse(self.request.GET['start'])
            to_date = dateutil.parser.parse(self.request.GET['end'])
            queryset = queryset.filter(end__gte=from_date, start__lt=to_date)

        return queryset


# TODO: only for admins
@login_required
def closing_post(request):
    location = None
    if 'location' in request.POST:
        location = Location.objects.get(pk=request.POST['location'])

    values = dict(
        start=request.POST['start'],
        end=request.POST['end'],
        location=location,
        is_global=(request.POST['is_global'] == 'true'),
        comment=request.POST['comment'])

    if 'id' in request.POST:
        Closing.objects.filter(pk=request.POST['id']).update(**values)
    else:
        Closing.objects.create(**values)

    return redirect('agenda:home')


# TODO: only for admins
@login_required
def closing_delete(request):
    Closing.objects.get(pk=request.POST['id']).delete()
    return redirect('agenda:home')
