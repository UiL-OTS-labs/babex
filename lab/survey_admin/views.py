import logging

from django.contrib.messages import error, success
from django.utils.translation import gettext as _
from django.views.generic import DetailView, ListView, TemplateView

from main.auth.util import IsRandomLeader
from participants.models import Participant
from participants.permissions import participants_visible_to_leader

from .models import SurveyDefinition, SurveyInvite

log = logging.getLogger()


class SurveyOverview(ListView):
    # TODO: permissions
    queryset = SurveyDefinition.objects.all()
    template_name = "survey_admin/index.html"


class SurveyPreview(DetailView):
    # TODO: permissions
    queryset = SurveyDefinition.objects.all()
    template_name = "survey_admin/preview.html"


class SurveyInviteParticipants(TemplateView):
    permission_classes = [IsRandomLeader]
    template_name = "survey_admin/invite.html"

    @property
    def survey(self):
        return SurveyDefinition.objects.get(pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["survey"] = self.survey
        context["object_list"] = self.get_participants()
        return context

    def get_participants(self):
        # TODO: exclude participants who already filled the survey?
        if self.request.user.is_staff:
            return Participant.objects.all()
        return participants_visible_to_leader(self.request.user)

    def post(self, request, *args, **kwargs):
        participant_ids = map(int, request.POST.getlist("participants"))

        failed = False
        for participant_id in participant_ids:
            participant = Participant.objects.get(pk=participant_id)
            invite, created = SurveyInvite.objects.get_or_create(participant=participant, survey=self.survey)
            try:
                invite.send()
            except Exception:
                log.exception("Failed sending survey invite: %d", invite.pk)
                failed = True
                error(request, _("survey_admin:message:invite_failure"))

        if not failed:
            success(request, _("survey_admin:message:invite_success"))
        return self.get(request)
