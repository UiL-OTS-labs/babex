from rest_framework import routers

from .views import ExperimentsView, LeaderExperimentsView

router = routers.DefaultRouter()
router.register('experiments', ExperimentsView, basename='experiments')
router.register('leader_experiments', LeaderExperimentsView,
                basename='leader_experiments')
