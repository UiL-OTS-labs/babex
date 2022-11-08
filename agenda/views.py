from datetime import timedelta, datetime
import dateutil.parser

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http.response import JsonResponse

from rest_framework import generics, views, serializers, viewsets
from rest_framework.response import Response

from experiments.models import Appointment, Location
from experiments.serializers import AppointmentSerializer
from .models import Closing, ClosingSerializer


class AppointmentFeed(generics.ListAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        from_date = dateutil.parser.parse(self.request.GET['start'])
        to_date = dateutil.parser.parse(self.request.GET['end'])
        return Appointment.objects.filter(timeslot__start__gte=from_date, timeslot__end__lt=to_date)


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

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        queryset = Appointment.objects.all()
        return queryset

