from django.conf.urls import include, url

from .views import (AddExistingCriteriumToExperimentView, CriteriaCreateView,
                    CriteriaDeleteView, CriteriaHomeView, CriteriaListView,
                    CriteriaUpdateView, DefaultCriteriaUpdateView,
                    ExperimentAppointmentsView, ExperimentCreateView,
                    ExperimentDeleteView, ExperimentEditExcludedExperimentsView,
                    ExperimentExcludeOtherExperimentView, ExperimentHomeView,
                    ExperimentSwitchOpenView, ExperimentSwitchPublicView,
                    ExperimentSwitchVisibleView, ExperimentUpdateView,
                    InviteParticipantsForExperimentView, LocationCreateView,
                    LocationHomeView, RemoveCriteriumFromExperiment,
                    SilentUnsubscribeParticipantView, TimeSlotBulkDeleteView,
                    TimeSlotDeleteView, TimeSlotHomeView,
                    UnsubscribeParticipantView, UpdateLocationView,
                    MailPreviewView)

# TODO: make this a little bit more readable

app_name = 'experiments'

urlpatterns = [
    url(r'^$', ExperimentHomeView.as_view(), name='home'),
    url(r'^new/$', ExperimentCreateView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/$', ExperimentUpdateView.as_view(), name='update'),
    url(r'^(?P<pk>\d+)/delete/$', ExperimentDeleteView.as_view(),
        name='delete'),

    # Participant in experiment view
    url(
        r'^(?P<experiment>\d+)/participants/$',
        ExperimentAppointmentsView.as_view(),
        name='participants',
    ),

    url(
        r'^(?P<experiment>\d+)/invite/$',
        InviteParticipantsForExperimentView.as_view(),
        name='invite',
    ),

    url(
        r'^(?P<experiment>\d+)/invite/preview/$',
        MailPreviewView.as_view(),
        name='mail_preview',
    ),

    # Excluded experiments views

    url(
        r'^(?P<experiment>\d+)/excluded_experiments/$',
        ExperimentEditExcludedExperimentsView.as_view(),
        name='excluded_experiments'
    ),
    url(
        r'^(?P<current_experiment>\d+)/exclude_experiment/('
        r'?P<exclude_experiment>\d+)/$',
        ExperimentExcludeOtherExperimentView.as_view(),
        name='exclude_experiment'
    ),

    # Experiment timeslot views

    url(
        r'^(?P<experiment>\d+)/timeslots/$',
        TimeSlotHomeView.as_view(),
        name='timeslots',
    ),

    url(
        r'^(?P<experiment>\d+)/timeslots/delete/(?P<timeslot>\d+)/$',
        TimeSlotDeleteView.as_view(),
        name='timeslots_delete',
    ),

    url(
        r'^(?P<time_slot>\d+)/timeslots/unsubscribe/(?P<appointment>\d+)/$',
        UnsubscribeParticipantView.as_view(),
        name='timeslots_unsubscribe',
    ),
    url(
        r'^(?P<time_slot>\d+)/timeslots/unsubscribe/silent/('
        r'?P<appointment>\d+)/$',
        SilentUnsubscribeParticipantView.as_view(),
        name='timeslots_unsubscribe_silent',
    ),

    url(
        r'^(?P<experiment>\d+)/timeslots/delete/$',
        TimeSlotBulkDeleteView.as_view(),
        name='timeslots_bulk_delete',
    ),

    # Experiment related criteria views

    url(
        r'^(?P<experiment>\d+)/default_criteria/$',
        DefaultCriteriaUpdateView.as_view(),
        name='default_criteria'
    ),

    url(
        r'^(?P<experiment>\d+)/criteria/$',
        CriteriaListView.as_view(),
        name='specific_criteria'
    ),
    url(
        r'^(?P<experiment>\d+)/criteria/remove/(?P<criterium>\d+)/$',
        RemoveCriteriumFromExperiment.as_view(),
        name='remove_criterium_from_experiment'
    ),
    url(
        r'^(?P<experiment>\d+)/criteria/add/$',
        AddExistingCriteriumToExperimentView.as_view(),
        name='add_criterium_to_experiment'
    ),

    # Experiment state switchers

    url(r'(?P<pk>\d+)/switch_open/', ExperimentSwitchOpenView.as_view(),
        name='switch_open'),
    url(r'(?P<pk>\d+)/switch_visible/', ExperimentSwitchVisibleView.as_view(),
        name='switch_visible'),
    url(r'(?P<pk>\d+)/switch_public/', ExperimentSwitchPublicView.as_view(),
        name='switch_public'),

    # Stand-alone location views

    url(r'^locations/', include([
        url(r'^$', LocationHomeView.as_view(), name='location_home'),
        url(r'^new/$', LocationCreateView.as_view(), name='location_create'),
        url(r'^(?P<pk>\d+)/$', UpdateLocationView.as_view(),
            name='location_update')
    ])),

    # Stand-alone criteria views

    url(r'^criteria/', include([
        url(r'^$', CriteriaHomeView.as_view(), name='criteria_home'),
        url(r'^new/$', CriteriaCreateView.as_view(), name='criterium_create'),
        url(r'^(?P<pk>\d+)/$', CriteriaUpdateView.as_view(),
            name='criterium_update'),
        url(r'^(?P<pk>\d+)/delete/$', CriteriaDeleteView.as_view(),
            name='criterium_delete'),
    ])),
]
