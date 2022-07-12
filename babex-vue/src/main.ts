import { createApp } from 'vue'
import AgendaCalendar from './components/agenda/AgendaCalendar.vue'


// using object.defineProperty instead of window.foo to satisfy typescript
Object.defineProperty(window, 'createApp', {value: createApp});

// any component that is used via the django {% vue %} tag should be registered as a global
Object.defineProperty(window, 'babex', {
    value:
    {
        AgendaCalendar,
    }
});
