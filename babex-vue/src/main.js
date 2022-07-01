import { createApp } from 'vue'
import AgendaCalendar from './components/AgendaCalendar.vue'

window.createApp = createApp;

// any component that is used via the django {% vue %} tag should be registered as a global
window.babex = {
    AgendaCalendar,
};
