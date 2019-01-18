import braces.views as braces
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy as reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .forms import LeaderCreateForm, LeaderUpdateForm
from .models import Leader
from .utils import create_leader, delete_leader, notify_new_leader, \
    update_leader

from django.db.models import Count, Q
from django.conf import settings


class LeaderHomeView(braces.RecentLoginRequiredMixin, generic.ListView):
    template_name = 'leaders/index.html'
    model = Leader

    def get_queryset(self):
        return self.model.objects.select_related(
            'api_user'
        ).annotate(
            # This will either be 0 or 1, thus a boolean. Annotating like
            # this saves a lot of DB queries
            active=Count(
                'api_user__groups',
                filter=Q(
                    api_user__groups__name=settings.LEADER_GROUP
                )
            )
        )


class LeaderCreateView(braces.RecentLoginRequiredMixin, SuccessMessageMixin,
                       generic.FormView):
    template_name = 'leaders/new.html'
    form_class = LeaderCreateForm
    success_url = reverse('leaders:home')
    success_message = _('leaders:create:success_message')

    def form_valid(self, form):
        """This method creates a new leader and if needed, notifies the new user
        of this action.
        """

        data = form.cleaned_data

        leader = create_leader(
            data['name'],
            data['email'],
            data['phonenumber'],
            data['password'],
        )

        if data['notify_user']:
            notify_new_leader(leader)

        return super(LeaderCreateView, self).form_valid(form)


class LeaderUpdateView(braces.RecentLoginRequiredMixin, SuccessMessageMixin,
                       generic.FormView):
    template_name = 'leaders/update.html'
    form_class = LeaderUpdateForm
    success_url = reverse('leaders:home')
    success_message = _('leaders:update:success_message')

    def get_initial(self):
        leader_pk = self.kwargs.pop('pk')
        leader = Leader.objects.get(pk=leader_pk)

        return {
            'name':        leader.name,
            'email':       leader.api_user.email,
            'phonenumber': leader.phonenumber,
            'leader':      leader,
            'active':      leader.is_active_leader(),
        }

    def form_valid(self, form):
        data = form.cleaned_data

        # Don't update password without explicit instruction
        if data['keep_current_password']:
            data['password'] = None

        update_leader(
            data['leader'],
            data['name'],
            data['email'],
            data['phonenumber'],
            data['password'],
            data['active'],
        )

        return super(LeaderUpdateView, self).form_valid(form)


class LeaderDeleteView(braces.RecentLoginRequiredMixin, generic.DetailView):
    template_name = 'leaders/delete.html'
    model = Leader

    def post(self, request, *args, **kwargs):
        object = self.get_object()

        delete_leader(object)

        messages.success(request, _('leaders:messages:deleted'))

        return HttpResponseRedirect(reverse('leaders:home'))
