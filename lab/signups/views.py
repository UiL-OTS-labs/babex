import braces.views as braces
from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from rest_framework import views
from rest_framework.response import Response

from participants.models import Participant
from signups.models import Signup


class SignupListView(braces.StaffuserRequiredMixin, ListView):
    queryset = Signup.objects.filter(status=Signup.Status.NEW, email_verified__isnull=False)

    def post(self, request, *args, **kwargs):
        """simple post endpoint for bulk-rejecting signups"""
        pks = map(int, request.POST.getlist("signups"))
        for signup in Signup.objects.filter(pk__in=pks):
            reject_signup(signup)
        return self.get(request, *args, **kwargs)


class SignupDetailView(braces.StaffuserRequiredMixin, DetailView):
    queryset = Signup.objects.all()

    def post(self, request, *args, **kwargs):
        action = self.request.POST["action"]
        signup = Signup.objects.get(pk=self.kwargs["pk"])
        if signup.status != Signup.Status.NEW:
            return HttpResponse("already processed")

        if action == "approve":
            approve_signup(signup)
            messages.success(request, _("signups:messages:approved"))
        elif action == "reject":
            reject_signup(signup)
            messages.success(request, _("signups:messages:rejected"))
        return redirect(reverse_lazy("signups:list"))


def approve_signup(signup: Signup):
    """Creates a new Participant record from a given Signup"""
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


class SignupVerifyView(views.APIView):
    def get(self, request, *args, **kwargs):
        signup = Signup.objects.get(link_token=kwargs["token"])
        signup.email_verified = timezone.now()
        signup.save()
        return Response(dict())
