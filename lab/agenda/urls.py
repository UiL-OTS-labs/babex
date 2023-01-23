from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import agenda_home
from .views import AppointmentFeed, ClosingViewSet, AppointmentViewSet, ClosingsAdminView

app_name = 'agenda'

urlpatterns = [
    path('', agenda_home, name='home'),
    path('feed', AppointmentFeed.as_view(), name='feed'),
    path('admin/closings', ClosingsAdminView.as_view(), name='admin.closings'),
]

router = DefaultRouter()
router.register('closing', ClosingViewSet, basename='closing')
router.register('appointment', AppointmentViewSet, basename='appointment')
urlpatterns += router.urls  # type: ignore
