from django.conf.urls import include
from django.urls import path

from ..views.email_views import email_preview

app_name = 'experiments'

urlpatterns = [
    path('', include('experiments.urls.experiments_urls')),

    # Participant in experiment view
    path('<int:experiment>/', include('experiments.urls.experiments_urls.participants')),

    # Excluded experiments views
    path('', include('experiments.urls.experiments_urls.excluded')),

    # Experiment timeslot views
    path('', include('experiments.urls.appointment_urls')),

    # Experiment related criteria views
    path('<int:experiment>/', include('experiments.urls.criteria_urls.experiment')),

    # Experiment state switchers
    path('<int:pk>/', include('experiments.urls.experiments_urls.state_switchers')),

    # Stand-alone location views
    path('locations/', include('experiments.urls.locations_urls')),

    # Stand-alone criteria views
    path('criteria/', include('experiments.urls.criteria_urls.standalone')),

    path('', include('experiments.urls.call_urls')),

    # email preview
    path('email/preview/<str:template>/<int:experiment>/', email_preview, name='email_preview'),
]
