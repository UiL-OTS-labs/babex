from django.contrib.auth.views import RedirectURLMixin
from django.http import Http404
from django.urls import reverse_lazy as reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views import generic

from main.auth.util import LabManagerMixin

from ..forms import DefaultCriteriaForm
from ..models import DefaultCriteria


class DefaultCriteriaUpdateView(LabManagerMixin, RedirectURLMixin, generic.UpdateView):
    template_name = "criteria/update_default.html"
    form_class = DefaultCriteriaForm
    model = DefaultCriteria

    pk_url_kwarg = "experiment"

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
            raise Http404(
                _("No %(verbose_name)s found matching the query") % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj

    def get_success_url(self):
        url = reverse("experiments:home")
        redirect_to = self.request.GET.get("next", url)

        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ""
