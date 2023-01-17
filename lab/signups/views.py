import braces.views as braces
from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView

from signups.models import Signup
from participants.models import Participant


class SignupListView(braces.LoginRequiredMixin, ListView):
    queryset = Signup.objects.filter(status=Signup.Status.NEW)

    def post(self, request, *args, **kwargs):
        '''simple post endpoint for bulk-rejecting signups'''
        pks = map(int, request.POST.getlist('signups'))
        for signup in Signup.objects.filter(pk__in=pks):
            reject_signup(signup)
        return self.get(request, *args, **kwargs)


class SignupDetailView(braces.LoginRequiredMixin, DetailView):
    queryset = Signup.objects.all()

    def post(self, request, *args, **kwargs):
        action = self.request.POST['action']
        signup = Signup.objects.get(pk=self.kwargs['pk'])
        if signup.status != Signup.Status.NEW:
            return HttpResponse('already processed')

        if action == 'approve':
            approve_signup(signup)
            messages.success(request, _('signups:messages:approved'))
        elif action == 'reject':
            reject_signup(signup)
            messages.success(request, _('signups:messages:rejected'))
        return redirect(reverse_lazy('signups:list'))


def approve_signup(signup: Signup):
    '''Creates a new Participant record from a given Signup'''
    Participant.objects.create(
        name=signup.name,
        sex=signup.sex,
        birth_date=signup.birth_date,
        parent_name=signup.parent_name,
        email=signup.email,
        phonenumber=signup.phonenumber,
        phonenumber_alt=signup.phonenumber_alt,
        city=signup.city,
        email_subscription=signup.newsletter,
        dyslexic_parent=signup.dyslexic_parent,
        multilingual=signup.multilingual,
    )

    signup.status = Signup.Status.APPROVED
    signup.save()


def reject_signup(signup: Signup):
    signup.status = Signup.Status.REJECTED
    signup.save()
