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
                         RedirectURLMixin,
                         DeleteSuccessMessageMixin,
                         generic.DeleteView):
    model = Comment
    success_message = _('comments:messages:deleted')
    template_name = 'comments/delete.html'

    def get_success_url(self):
        url = reverse('comments:home')
        redirect_to = self.request.GET.get('next', url)

        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''
