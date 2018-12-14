from django.views import generic
from django.utils.text import gettext_lazy as _
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy as reverse
import braces.views as braces

from .models import Comment
from .forms import CommentForm
from uil.core.views.mixins import DeleteSuccessMessageMixin


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

    def get_initial(self):
        initial = super(CommentCreateView, self).get_initial()

        initial['experiment'] = self.kwargs.get('experiment')
        initial['participant'] = self.kwargs.get('participant')

        return initial

    def get_success_url(self):
        args = [self.kwargs.get('experiment'), ]
        return reverse('experiments:participants', args=args)


class CommentsDeleteView(braces.LoginRequiredMixin,
                         DeleteSuccessMessageMixin, generic.DeleteView):
    model = Comment
    success_url = reverse('comments:home')
    success_message = _('comments:messages:deleted')
    template_name = 'comments/delete.html'
