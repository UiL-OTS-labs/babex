from django.urls import path

from ..views import (SilentUnsubscribeParticipantView, TimeSlotBulkDeleteView,
                     TimeSlotDeleteView, TimeSlotHomeView,
                     UnsubscribeParticipantView, )

urlpatterns = [
    path(
        '<int:experiment>/timeslots/',
        TimeSlotHomeView.as_view(),
        name='timeslots',
    ),

    path(
        '<int:experiment>/timeslots/delete/<int:timeslot>/',
        TimeSlotDeleteView.as_view(),
        name='timeslots_delete',
    ),

    path(
        '<int:experiment>/unsubscribe/<int:appointment>)/',
        UnsubscribeParticipantView.as_view(),
        name='unsubscribe',
    ),
    path(
        '<int:experiment>/unsubscribe/silent/<int:appointment>/',
        SilentUnsubscribeParticipantView.as_view(),
        name='unsubscribe_silent',
    ),

    path(
        '<int:experiment>/timeslots/delete/',
        TimeSlotBulkDeleteView.as_view(),
        name='timeslots_bulk_delete',
    ),
]
