import braces.views as braces
from django.urls import reverse_lazy as reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views import generic

from uil.core.views import RedirectActionView
from uil.core.views.mixins import RedirectSuccessMessageMixin

from datamanagement.utils.comments import get_comment_counts
from datamanagement.utils.invitations import get_invite_counts
from datamanagement.utils.participants import get_old_participants
from experiments.models import Experiment

# TODO: confirmation dialogs, settings, write tests


class OverviewView(braces.LoginRequiredMixin, generic.TemplateView):
    template_name = 'datamanagement/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['invites'] = get_invite_counts()
        context['comments'] = get_comment_counts()
        context['participants'] = get_old_participants()

        return context


class DeleteInvitesView(braces.LoginRequiredMixin,
                        RedirectSuccessMessageMixin,
                        RedirectActionView):
    url = reverse('datamanagement:overview')

    def action(self, request):
        pass # TODO: actually delete stuff

    @cached_property
    def experiment(self):
        pk = self.kwargs.get('experiment')

        return Experiment.objects.get(pk=pk)

    def get_success_message(self):
        return _('datamanagement:messages:deleted_invites').format(
            self.experiment
        )


class DeleteCommentsView(braces.LoginRequiredMixin,
                         RedirectSuccessMessageMixin,
                         RedirectActionView):
    url = reverse('datamanagement:overview')

    def action(self, request):
        pass # TODO: actually delete stuff

    @cached_property
    def experiment(self):
        pk = self.kwargs.get('experiment')

        return Experiment.objects.get(pk=pk)

    def get_success_message(self):
        return _('datamanagement:messages:deleted_comments').format(
            self.experiment
        )
