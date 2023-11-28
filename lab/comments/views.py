import braces.views as braces
from cdh.core.views.mixins import DeleteSuccessMessageMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy as reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from main.auth.util import RandomLeaderMixin
from participants.models import Participant
from participants.permissions import can_leader_access_participant

from .forms import CommentForm
from .models import Comment


class CommentCreateView(RandomLeaderMixin, SuccessMessageMixin, generic.CreateView):
    template_name = "comments/new.html"
    form_class = CommentForm
    model = Comment
    success_message = _("comments:messages:created")

    @property
    def participant(self):
        pk = int(self.request.POST["participant"])
        return Participant.objects.get(pk=pk)

    def test_func(self, user):
        return can_leader_access_participant(user, self.participant)

    def get_success_url(self):
        return reverse("participants:detail", args=(self.participant.pk,))

    def form_valid(self, form):
        # force the leader field to match current user
        form.instance.leader = self.request.user
        return super().form_valid(form)


class CommentsDeleteView(braces.UserPassesTestMixin, DeleteSuccessMessageMixin, generic.DeleteView):
    model = Comment
    success_message = _("comments:messages:deleted")

    def get_success_url(self):
        return reverse("participants:detail", args=(self.object.participant.pk,))

    def test_func(self, user):
        return user.is_superuser or user == self.object.leader
