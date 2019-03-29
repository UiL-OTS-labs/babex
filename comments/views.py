import braces.views as braces
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy as reverse
from django.utils.text import gettext_lazy as _
from django.views import generic
from uil.core.views.mixins import DeleteSuccessMessageMixin

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

    def get_initial(self):
        initial = super(CommentCreateView, self).get_initial()

        initial['experiment'] = self.kwargs.get('experiment')
        initial['participant'] = self.kwargs.get('participant')

        return initial

    def form_valid(self, form):
        form.instance.experiment_id = self.kwargs.get('experiment')
        form.instance.participant_id = self.kwargs.get('participant')

        return super(CommentCreateView, self).form_valid(form)

    def get_success_url(self):
        args = [self.kwargs.get('experiment'), ]
        return reverse('experiments:participants', args=args)


class CommentsDeleteView(braces.LoginRequiredMixin,
                         DeleteSuccessMessageMixin, generic.DeleteView):
    model = Comment
    success_url = reverse('comments:home')
    success_message = _('comments:messages:deleted')
    template_name = 'comments/delete.html'
