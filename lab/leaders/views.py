import braces.views as braces
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy as reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from main.utils import is_ldap_enabled
from .forms import LDAPLeaderCreateForm, LeaderCreateForm, LeaderUpdateForm, \
    LDAPLeaderUpdateForm
from .models import Leader
from .utils import create_ldap_leader, create_leader, \
    delete_leader, \
    notify_new_ldap_leader, notify_new_leader, update_leader


class LeaderHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'leaders/index.html'
    model = Leader

    def get_queryset(self):
        return self.model.objects.select_related(
            'user'
        ).annotate(
            # This will either be 0 or 1, thus a boolean. Annotating like
            # this saves a lot of DB queries
            active=Count(
                'user__groups',
                filter=Q(
                    user__groups__name=settings.LEADER_GROUP
                )
            )
        )

    def get_context_data(self, *args, **kwargs):
        context = super(LeaderHomeView, self).get_context_data(*args, **kwargs)

        context['ldap'] = is_ldap_enabled()

        return context


class LeaderCreateView(braces.LoginRequiredMixin, SuccessMessageMixin,
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

        leader, existing = create_leader(
            data['name'],
            data['email'],
            data['phonenumber'],
            data['password'],
        )

        if data['notify_user']:
            notify_new_leader(leader, existing)

        return super(LeaderCreateView, self).form_valid(form)


class LDAPLeaderCreateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                           generic.FormView):
    template_name = 'leaders/new.html'
    form_class = LDAPLeaderCreateForm
    success_url = reverse('leaders:home')
    success_message = _('leaders:create:success_message')

    def form_valid(self, form):
        """This method creates a new leader and if needed, notifies the new user
        of this action.
        """

        data = form.cleaned_data

        leader = create_ldap_leader(
            data['name'],
            data['email'],
            data['phonenumber'],
        )

        if data['notify_user']:
            notify_new_ldap_leader(leader)

        return super(LDAPLeaderCreateView, self).form_valid(form)


class LeaderUpdateView(braces.LoginRequiredMixin, SuccessMessageMixin,
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


class LDAPLeaderUpdateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                           generic.FormView):
    template_name = 'leaders/update.html'
    form_class = LDAPLeaderUpdateForm
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

        update_leader(
            data['leader'],
            data['name'],
            data['email'],
            data['phonenumber'],
            None,
            data['active'],
        )

        return super(LDAPLeaderUpdateView, self).form_valid(form)


class LeaderDeleteView(braces.LoginRequiredMixin, generic.DetailView):
    template_name = 'leaders/delete.html'
    model = Leader

    def post(self, request, *args, **kwargs):
        object = self.get_object()

        delete_leader(object)

        messages.success(request, _('leaders:messages:deleted'))

        return HttpResponseRedirect(reverse('leaders:home'))
