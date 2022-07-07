from datetime import timedelta
import braces.views as braces

from django.views.generic import TemplateView

from experiments.models import Appointment


class AgendaHomeView(braces.LoginRequiredMixin, TemplateView):
    template_name = 'agenda/home.html'

    def format_appointment(self, appointment):
        return dict(
            start=appointment.timeslot.datetime,
            end=appointment.timeslot.datetime + timedelta(hours=1),
            experiment=appointment.experiment.name,
            leader=appointment.timeslot.experiment.leader.name,
            participant=appointment.participant.name,
            location=appointment.timeslot.experiment.location.name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['events'] = [self.format_appointment(x)
                             for x in Appointment.objects.all()]
        return context
