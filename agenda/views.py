from datetime import timedelta, datetime
import dateutil.parser

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http.response import JsonResponse

from experiments.models import Appointment, Location
from .models import Closing


def agenda_context(from_date, to_date):
    context = dict()
    appointments = Appointment.objects.filter(timeslot__datetime__gte=from_date, timeslot__datetime__lt=to_date)
    closings = Closing.objects.filter(end__gte=from_date, start__lt=to_date)


    # TODO: these format methods don't belong here, they should be more generic
    def format_appointment(appointment):
        return dict(
            id=appointment.id,
            start=appointment.timeslot.datetime,
            end=appointment.timeslot.datetime + timedelta(hours=1),
            experiment=appointment.experiment.name,
            leader=appointment.timeslot.experiment.leader.name,
            participant=appointment.participant.name,
            location=appointment.timeslot.experiment.location.name)

    def format_closing(closing):
        return dict(
            id=closing.id,
            start=closing.start,
            end=closing.end,
            is_global=closing.is_global,
            location=closing.location.name if closing.location else None,
            comment=closing.comment)


    context['appointments'] = [format_appointment(x) for x in appointments]
    context['closings'] = [format_closing(x) for x in closings]
    context['from'] = from_date
    context['to'] = to_date
    return context


@login_required
def agenda_feed(request):
    from_date = dateutil.parser.parse(request.GET['from'])
    to_date = dateutil.parser.parse(request.GET['to'])
    return JsonResponse(agenda_context(from_date, to_date))


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
