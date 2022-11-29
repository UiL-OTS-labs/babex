import braces.views as braces
from django.urls import reverse_lazy as reverse
from django.utils.translation import gettext as _
from django.views import generic

from participants.models import Participant
from cdh.core.views import RedirectActionView
from cdh.core.views.mixins import RedirectSuccessMessageMixin


from datamanagement.forms import ThresholdsEditForm
from datamanagement.utils.common import get_thresholds_model
from datamanagement.utils.invitations import delete_invites, get_invite_counts
from datamanagement.utils.participants import \
    delete_participant, get_participants_with_appointments, \
    get_participants_without_appointments
from experiments.models import Experiment


# TODO: write tests


class OverviewView(braces.LoginRequiredMixin, generic.TemplateView):
    template_name = 'datamanagement/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['invites'] = get_invite_counts()
        context['participants'] = get_participants_with_appointments()
        context['participants_no_app'] = get_participants_without_appointments()
        context['participants_num'] = len(context['participants']) + \
            len(context['participants_no_app'])

        return context


class ThresholdsEditView(braces.LoginRequiredMixin, generic.UpdateView):
    form_class = ThresholdsEditForm
    template_name = 'datamanagement/edit_thresholds.html'
    success_url = reverse('datamanagement:overview')

    def get_object(self, queryset=None):
        return get_thresholds_model()


class DeleteParticipantView(braces.LoginRequiredMixin,
                            RedirectSuccessMessageMixin,
                            RedirectActionView):

    def action(self, request):

        if delete_participant(self.participant, self.request.user):
            self.success_message = _(
                'datamanagement:messages:deleted_participant'
            )
        else:
            self.success_message = _('datamanagement:messages:refused_deletion')

    @property
    def participant(self):
        pk = self.kwargs.get('participant')

        return Participant.objects.get(pk=pk)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('datamanagement:overview') + "#collapse-participants"


class DeleteInvitesView(braces.LoginRequiredMixin,
                        RedirectSuccessMessageMixin,
                        RedirectActionView):

    def action(self, request):
        delete_invites(self.experiment, self.request.user)

    @property
    def experiment(self):
        pk = self.kwargs.get('experiment')

        return Experiment.objects.get(pk=pk)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('datamanagement:overview') + "#collapse-invites"

    def get_success_message(self):
        return _('datamanagement:messages:deleted_invites').format(
            self.experiment
        )
