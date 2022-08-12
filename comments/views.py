import braces.views as braces
from django.contrib.auth.views import RedirectURLMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy as reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.text import gettext_lazy as _
from django.views import generic
from cdh.core.views.mixins import DeleteSuccessMessageMixin

from .forms import CommentForm
from .models import Comment


class CommentsHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'comments/index.html'
    model = Comment

    def get_queryset(self):
        """Return a queryset that's been instructed to also pull the related
        objects. This makes this page around 10 times faster"""
        return self.model.objects.select_related('participant', 'leader',
                                                 'experiment')


class CommentCreateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                        generic.CreateView):
    template_name = 'comments/new.html'
    form_class = CommentForm
    success_message = _('comments:messages:created')

    def get_success_url(self):
        return reverse('participants:detail', args=(self.object.participant.pk,))


class CommentsDeleteView(braces.UserPassesTestMixin,
                         RedirectURLMixin,
                         DeleteSuccessMessageMixin,
                         generic.DeleteView):
    model = Comment
    success_message = _('comments:messages:deleted')
    template_name = 'comments/delete.html'

    def get_success_url(self):
        return reverse('participants:detail', args=(self.object.participant.pk,))

    def test_func(self, user):
        return user.is_superuser or user == self.object.leader
