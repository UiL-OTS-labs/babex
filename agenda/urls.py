from django.urls import path
from django.views.generic import TemplateView

from .views import agenda_home, agenda_success
from .views import AppointmentFeed, AppointmentInfo, AppointmentAddView
from .views import ClosingFeed, ClosingAddView, ClosingEditView, ClosingDeleteView

app_name = 'agenda'

urlpatterns = [
    path('', agenda_home, name='home'),

    path('feed', AppointmentFeed.as_view(), name='feed'),
    path('appointment/add/<experiment>', AppointmentAddView.as_view(), name='appointment.add'),
    path('appointment/<pk>', AppointmentInfo.as_view(), name='appointment.info'),

    path('closing/', ClosingFeed.as_view(), name='closing'),
    path('closing/add', ClosingAddView.as_view(), name='closing.add'),
    path('closing/<pk>/', ClosingEditView.as_view(), name='closing.edit'),
    path('closing/<pk>/delete', ClosingDeleteView.as_view(), name='closing.delete'),

    path('success', agenda_success, name='success')
]
