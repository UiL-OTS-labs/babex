from django.conf.urls import include
from django.urls import path

from ..views.email_views import email_preview

app_name = "experiments"

urlpatterns = [
    path("", include("experiments.urls.experiments_urls")),
    # Participant in experiment view
    path("<int:experiment>/", include("experiments.urls.experiments_urls.participants")),
    # Experiment related criteria views
    path("<int:experiment>/", include("experiments.urls.criteria_urls.experiment")),
    # Stand-alone location views
    path("locations/", include("experiments.urls.locations_urls")),
    # Stand-alone criteria views
    path("criteria/", include("experiments.urls.criteria_urls.standalone")),
    path("", include("experiments.urls.call_urls")),
    # email preview
    path("email/preview/<str:template>/<int:experiment>/", email_preview, name="email_preview"),
]
