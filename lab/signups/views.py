from datetime import timedelta

import braces.views as braces
from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone, translation
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from rest_framework import views
from rest_framework.response import Response

from main.auth.util import LabManagerMixin
from participants.models import Language, Participant
from signups.models import Signup


class SignupListView(LabManagerMixin, ListView):
    queryset = Signup.objects.filter(status=Signup.Status.NEW, email_verified__isnull=False)

    def post(self, request, *args, **kwargs):
        """simple post endpoint for bulk-rejecting signups"""
        pks = map(int, request.POST.getlist("signups"))
        for signup in Signup.objects.filter(pk__in=pks):
            reject_signup(signup)
        return self.get(request, *args, **kwargs)


class SignupDetailView(braces.StaffuserRequiredMixin, DetailView):
    queryset = Signup.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["languages"] = Language.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        action = self.request.POST["action"]
        signup = Signup.objects.get(pk=self.kwargs["pk"])
        languages = self.request.POST.getlist("languages")
        signup.languages = [lang.strip() for lang in languages]
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
    # resolve languages field
    languages = []
    for language in signup.languages:
        lang, created = Language.objects.get_or_create(name=language)
        languages.append(lang)

    participant = Participant.objects.create(
        name=signup.name,
        sex=signup.sex,
        birth_date=signup.birth_date,
        birth_weight=signup.birth_weight,
        pregnancy_duration=signup.pregnancy_duration,
        parent_first_name=signup.parent_first_name,
        parent_last_name=signup.parent_last_name,
        email=signup.email,
        phonenumber=signup.phonenumber,
        phonenumber_alt=signup.phonenumber_alt,
        dyslexic_parent=signup.dyslexic_parent,
        tos_parent=signup.tos_parent,
        save_longer=signup.save_longer,
        english_contact=signup.english_contact,
        email_subscription=signup.newsletter,
    )
    participant.languages.set(languages)

    signup.status = Signup.Status.APPROVED
    signup.save()


def reject_signup(signup: Signup):
    signup.status = Signup.Status.REJECTED
    signup.save()


class SignupVerifyView(views.APIView):
    def get(self, request, *args, **kwargs):
        signup = Signup.objects.get(link_token=kwargs["token"])
        if timezone.now() - signup.created > timedelta(days=1):
            # expired
            with translation.override("nl"):
                return Response(dict(reason=gettext("signups:verify:error:expired")), status=410)
        else:
            signup.email_verified = timezone.now()
            signup.save()
            return Response(dict())
