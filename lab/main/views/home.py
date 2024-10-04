import braces.views as braces
from django.utils import timezone
from django.views import generic

from experiments.models.invite_models import Call
from signups.models import Signup


class HomeView(braces.LoginRequiredMixin, generic.TemplateView):
    template_name = "main/index.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        if self.request.user.is_leader:
            context["experiments"] = user.experiments.all()
            call_back = user.call_set.filter(status=Call.CallStatus.CALLBACK)
            last_per_pp = dict()
            for call in call_back:
                if call.participant not in last_per_pp or call.creation_date > last_per_pp[call.participant]:
                    last_per_pp[call.participant] = call

            context["call_back"] = last_per_pp.values()
            context["open_calls"] = user.call_set.filter(status=Call.CallStatus.STARTED)
            context["missing_outcome"] = (
                user.appointment_set.filter(outcome=None)
                .filter(timeslot__start__lte=timezone.now())
                .order_by("-timeslot__start")
            )

            if self.request.user.is_staff:
                context["signups"] = Signup.objects.filter(
                    status=Signup.Status.NEW, email_verified__isnull=False
                ).count()

        return context
