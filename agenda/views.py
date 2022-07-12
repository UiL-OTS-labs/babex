from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from experiments.models import Appointment, Location
from .models import Closing


@login_required
def agenda_home(request):
    context = dict()
    appointments = Appointment.objects.all()
    closings = Closing.objects.all()
    locations = Location.objects.all()

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

    def format_location(location):
        return dict(
            id=location.id,
            name=location.name)

    context['appointments'] = [format_appointment(x) for x in appointments]
    context['closings'] = [format_closing(x) for x in closings]
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
