import { createApp } from 'vue'
import AgendaCalendar from './components/agenda/AgendaCalendar.vue'
import AgendaHome from './components/agenda/AgendaHome.vue'
import CallHome from './components/invite/CallHome.vue'
import SurveyView from './components/survey/SurveyView.vue'
import ParentSurveyView from './components/survey/ParentSurveyView.vue'
import CancelAppointment from './components/parent/CancelAppointment.vue'
import ParticipantDemographics from './components/participants/ParticipantDemographics.vue'
import * as Toaster from './toaster'


// using object.defineProperty instead of window.foo to satisfy typescript
Object.defineProperty(window, 'createApp', {value: createApp});

// any component that is used via the django {% vue %} tag should be registered as a global
Object.defineProperty(window, 'babex', {
    value:
    {
        AgendaCalendar,
        AgendaHome,

        CallHome,

        SurveyView,
        ParentSurveyView,
        CancelAppointment,

        ParticipantDemographics
    }
});


// register a global handler for uncaught promise rejections
window.addEventListener('unhandledrejection', function (error) {
    Toaster.error(error.reason);
});
