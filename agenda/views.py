from datetime import timedelta
import braces.views as braces

from django.views.generic import TemplateView

from experiments.models import TimeSlot


class AgendaHomeView(braces.LoginRequiredMixin, TemplateView):
    template_name = 'agenda/home.html'

    def format_slot(self, timeslot):
        return dict(
            start=timeslot.datetime,
            end=timeslot.datetime + timedelta(hours=1),
            experiment=timeslot.experiment.name,
            leader=timeslot.experiment.leader.name,
            location=timeslot.experiment.location.name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # as a quick test, I'm displaying time slots instead of appointments
        # because that already exists in the app
        context['timeslots'] = [self.format_slot(s) for s in TimeSlot.objects.all()]
        return context
