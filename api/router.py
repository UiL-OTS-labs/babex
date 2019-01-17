from rest_framework import routers

from .views import OpenExperimentsView, LeaderExperimentsView

router = routers.DefaultRouter()
router.register('experiments', OpenExperimentsView, basename='experiments')
router.register('leader_experiments', LeaderExperimentsView,
                basename='leader_experiments')
