from django.urls import path
from django.views.generic import TemplateView

from .views import link_verify, LoginFormView, resolve_pp

app_name = 'mailauth'

urlpatterns = [
    path("sent", TemplateView.as_view(template_name='mailauth/sent.html'), name='sent'),
    #
    path("", LoginFormView.as_view(), name='home'),
    path("resolve/<participant_id>/", resolve_pp, name='resolve'),
    # has to be last
    path("<str:token>", link_verify),
]
