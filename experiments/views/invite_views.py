import braces.views as braces
from django.contrib.messages import error, success
from django.core.exceptions import ViewDoesNotExist
from django.utils.translation import ugettext as _
from django.views import generic

from experiments.utils.invite import _parse_contents_html as parse_contents, \
    get_invite_mail_content, mail_invite
from main.utils import get_supreme_admin
from .mixins import ExperimentObjectMixin
from ..utils.exclusion import get_eligible_participants_for_experiment


class InviteParticipantsForExperimentView(braces.LoginRequiredMixin,
                                          ExperimentObjectMixin,
                                          generic.TemplateView):
    template_name = 'experiments/invite.html'

    experiment_prefetch_related = ['experimentcriterion_set',
                                   'experimentcriterion_set__criterion',
                                   'additional_leaders']
    experiment_select_related = ['defaultcriteria', 'leader', ]

    def get_context_data(self, **kwargs):
        context = super(InviteParticipantsForExperimentView,
                        self).get_context_data(**kwargs)

        context['object_list'] = get_eligible_participants_for_experiment(
            self.experiment
        )
        context['experiment'] = self.experiment
        context['admin'] = get_supreme_admin().get_full_name()
        context['invite_text'] = get_invite_mail_content(self.experiment)

        return context

    def post(self, request, *args, **kwargs):
        data = request.POST
        failed = False

        try:
            mail_invite(
                data.getlist('participants[]'),
                data.get('content'),
                self.experiment
            )
        except:
            failed = True

        if failed:
            error(request, _('experiments:message:invite_failure'))
        else:
            success(request, _('experiments:message:invite_success'))

        return self.get(request)


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
        context['preview'] = True

        content = self.request.POST.get('content')
        context['content'] = parse_contents(content, self.experiment)

        return context
