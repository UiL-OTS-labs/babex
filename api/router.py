from rest_framework import routers

from .views import OpenExperimentsView

router = routers.DefaultRouter()
router.register('experiments', OpenExperimentsView, basename='api')
