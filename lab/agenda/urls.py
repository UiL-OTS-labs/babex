from django.urls import path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    AgendaHome,
    AppointmentFeed,
    AppointmentViewSet,
    ClosingsAdminView,
    ClosingViewSet,
)

app_name = "agenda"

urlpatterns = [
    path("", AgendaHome.as_view(), name="home"),
    path("feed", AppointmentFeed.as_view(), name="feed"),
    path("admin/closings", ClosingsAdminView.as_view(), name="admin.closings"),
    re_path(r"(?P<date>\d{4}-\d{2}-\d{2})/", AgendaHome.as_view(), name="agenda.date"),
]

router = DefaultRouter()
router.register("closing", ClosingViewSet, basename="closing")
router.register("appointment", AppointmentViewSet, basename="appointment")
urlpatterns += router.urls  # type: ignore
