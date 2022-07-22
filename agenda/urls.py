from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import agenda_home, closing_post, closing_delete
from .views import AppointmentFeed, ClosingViewSet

app_name = 'agenda'

urlpatterns = [
    path('', agenda_home, name='home'),
    path('feed', AppointmentFeed.as_view(), name='feed'),
]

router = DefaultRouter()
router.register('closing', ClosingViewSet, basename='closing')
urlpatterns += router.urls
