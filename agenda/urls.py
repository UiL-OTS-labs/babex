from django.urls import path
from django.views.generic import TemplateView

from .views import agenda_home
from .views import AppointmentFeed, AppointmentInfo
from .views import ClosingFeed, ClosingAddView, ClosingEditView, ClosingDeleteView

app_name = 'agenda'

urlpatterns = [
    path('', agenda_home, name='home'),
    path('feed', AppointmentFeed.as_view(), name='feed'),
    path('appointment/<pk>', AppointmentInfo.as_view(), name='appointment.info'),

    path('closing/', ClosingFeed.as_view(), name='closing'),
    path('closing/add', ClosingAddView.as_view(), name='closing.add'),
    path('closing/<pk>/', ClosingEditView.as_view(), name='closing.edit'),
    path('closing/<pk>/delete', ClosingDeleteView.as_view(), name='closing.delete'),

    path('success', TemplateView.as_view(template_name='agenda/success.html'), name='success')
]
