import braces.views as braces
from django.contrib.messages import error, success
from django.core.exceptions import ObjectDoesNotExist, ViewDoesNotExist
from django.utils.translation import gettext as _
from django.views import generic

from experiments.utils.invite import _parse_contents_html as parse_contents
from experiments.utils.invite import get_invite_mail_content, mail_invite
from main.auth.util import ExperimentLeaderMixin, RandomLeaderMixin

from ..utils.exclusion import get_eligible_participants_for_experiment
from .mixins import ExperimentObjectMixin


class InviteParticipantsForExperimentView(ExperimentLeaderMixin, ExperimentObjectMixin, generic.TemplateView):
    template_name = "experiments/invite.html"

    def get_context_data(self, **kwargs):
        context = super(InviteParticipantsForExperimentView, self).get_context_data(**kwargs)

        context["object_list"] = self.get_object_list()
        context["experiment"] = self.experiment
        context["is_leader"] = self.experiment in self.request.user.experiments.all()

        inviting_leader = self.request.user
        context["invite_text"] = get_invite_mail_content(self.experiment, inviting_leader)

        return context

    def get_object_list(self):
        particitants = get_eligible_participants_for_experiment(self.experiment)

        for participant in particitants:
            try:
                invite = (
                    participant.invitation_set.filter(experiment=self.experiment).order_by("-creation_date").first()
                )
                participant.invite = invite
            except ObjectDoesNotExist:
                participant.invite = None

        return particitants

    def post(self, request, *args, **kwargs):
        data = request.POST
        failed = False

        try:
            mail_invite(data.getlist("participants[]"), data.get("content"), self.experiment)
        except Exception:
            failed = True

        if failed:
            error(request, _("experiments:message:invite_failure"))
        else:
            success(request, _("experiments:message:invite_success"))

        return self.get(request)


class MailPreviewView(RandomLeaderMixin, ExperimentObjectMixin, generic.TemplateView):
    template_name = "experiments/mail/invite.html"

    def get(self, request, *args, **kwargs):
        raise ViewDoesNotExist

    def post(self, request, *args, **kwargs):
        return super(MailPreviewView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MailPreviewView, self).get_context_data(**kwargs)

        context["experiment"] = self.experiment
        context["preview"] = True

        content = self.request.POST.get("content")
        context["content"] = parse_contents(content, self.experiment)

        return context
