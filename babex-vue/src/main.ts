import { createApp } from 'vue'
import AgendaCalendar from './components/agenda/AgendaCalendar.vue'
import AgendaHome from './components/agenda/AgendaHome.vue'
import * as Toaster from './toaster'


// using object.defineProperty instead of window.foo to satisfy typescript
Object.defineProperty(window, 'createApp', {value: createApp});

// any component that is used via the django {% vue %} tag should be registered as a global
Object.defineProperty(window, 'babex', {
    value:
    {
        AgendaCalendar,
        AgendaHome
    }
});


// register a global handler for uncaught promise rejections
window.addEventListener('unhandledrejection', function (error) {
    Toaster.error(error.reason);
});
