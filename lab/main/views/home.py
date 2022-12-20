import braces.views as braces
from django.views import generic

from experiments.models.invite_models import Call


class HomeView(braces.LoginRequiredMixin, generic.TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        context['experiments'] = user.leader.experiments.all()
        context['call_back'] = set(call.participant for call in
                                   user.leader.call_set.filter(status=Call.CallStatus.CALLBACK))

        return context
