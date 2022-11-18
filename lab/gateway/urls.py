from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import GatewayHome
from .views import Signups


router = DefaultRouter()
router.register('signup', Signups, basename='signup')

urlpatterns = [
    path('', GatewayHome.as_view(), name='home'),
    path('', include(router.urls)),
]
