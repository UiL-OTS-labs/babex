import braces.views as braces
from django.core.exceptions import ViewDoesNotExist
from django.utils.text import mark_safe
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .mixins import ExperimentObjectMixin
from main.utils import get_supreme_admin
from ..utils.exclusion import get_eligible_participants_for_experiment


class InviteParticipantsForExperimentView(braces.LoginRequiredMixin,
                                          ExperimentObjectMixin,
                                          generic.TemplateView):
    template_name = 'experiments/invite.html'

    experiment_prefetch_related = ['experimentcriterium_set',
                                   'experimentcriterium_set__criterium',
                                   'additional_leaders']
    experiment_select_related = ['defaultcriteria', 'leader',]

    def get_context_data(self, **kwargs):
        context = super(InviteParticipantsForExperimentView,
                        self).get_context_data(**kwargs)

        context['object_list'] = get_eligible_participants_for_experiment(
            self.experiment
        )
        context['experiment'] = self.experiment
        context['admin'] = get_supreme_admin().get_full_name()

        return context


class MailPreviewView(braces.LoginRequiredMixin, ExperimentObjectMixin,
                      generic.TemplateView):
    template_name = 'experiments/mail/invite.html'

    def get(self, request, *args, **kwargs):
        raise ViewDoesNotExist

    def post(self, request, *args, **kwargs):
        return super(MailPreviewView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MailPreviewView, self).get_context_data(**kwargs)

        context['experiment'] = self.experiment

        content = self.request.POST.get('content')
        context['content'] = mark_safe(content)

        return context
