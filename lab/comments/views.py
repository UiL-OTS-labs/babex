import braces.views as braces
from cdh.core.views.mixins import DeleteSuccessMessageMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy as reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from main.auth.util import RandomLeaderMixin
from participants.permissions import can_leader_access_participant

from .forms import CommentForm
from .models import Comment


class CommentCreateView(RandomLeaderMixin, SuccessMessageMixin, generic.CreateView):
    template_name = "comments/new.html"
    form_class = CommentForm
    success_message = _("comments:messages:created")

    def test_func(self, user):
        return can_leader_access_participant(user, self.object.participant)

    def get_success_url(self):
        return reverse("participants:detail", args=(self.object.participant.pk,))


class CommentsDeleteView(braces.UserPassesTestMixin, DeleteSuccessMessageMixin, generic.DeleteView):
    model = Comment
    success_message = _("comments:messages:deleted")

    def get_success_url(self):
        return reverse("participants:detail", args=(self.object.participant.pk,))

    def test_func(self, user):
        return user.is_superuser or user == self.object.leader
