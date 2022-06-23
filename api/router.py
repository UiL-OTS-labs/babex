from rest_framework import routers

from .views import AppointmentsView, ExperimentsView, LeaderExperimentsView

router = routers.DefaultRouter()
router.register('experiments', ExperimentsView, basename='experiments')
router.register('leader_experiments', LeaderExperimentsView,
                basename='leader_experiments')
router.register('participant/appointments', AppointmentsView,
                basename='appointments')
