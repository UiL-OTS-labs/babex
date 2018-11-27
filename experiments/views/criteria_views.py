from django.http import Http404
from django.views import generic
from django.urls import reverse
import braces.views as braces

from ..models import DefaultCriteria
from ..forms import DefaultCriteriaForm


class UpdateDefaultCriteriaView(braces.LoginRequiredMixin, generic.UpdateView):
    template_name = 'criteria/update_default.html'
    form_class = DefaultCriteriaForm
    model = DefaultCriteria

    pk_url_kwarg = 'experiment'

    def get_object(self, queryset=None):
        """
        Overrides the default get_object because that one assumes that we we
        always use the pk to get the object _for some reason_
        """

        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg)

        kwargs = {self.pk_url_kwarg: pk}

        if pk is not None:
            queryset = queryset.filter(**kwargs)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_success_url(self):
        return reverse('experiments:home')
