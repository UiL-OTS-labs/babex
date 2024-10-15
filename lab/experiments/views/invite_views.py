import braces.views as braces
from django.contrib.messages import error, success
from django.core.exceptions import ObjectDoesNotExist, ViewDoesNotExist
from django.utils.translation import gettext as _
from django.views import generic

from experiments.utils.invite import _parse_contents_html as parse_contents
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
        return context

    def get_object_list(self):
        particitants = get_eligible_participants_for_experiment(self.experiment)

        for participant in particitants:
            try:
                invite = (
                    participant.invitation_set.filter(experiment=self.experiment).order_by("-creation_date").first()
                )
                participant.invite = invite

                participant.last_call = (
                    participant.call_set.filter(experiment=self.experiment).order_by("-creation_date").first()
                )
            except ObjectDoesNotExist:
                participant.invite = None

        return particitants
