<script>
    import '@fullcalendar/core/vdom' // solves problem with Vite
    import FullCalendar from '@fullcalendar/vue3'
    import dayGridPlugin from '@fullcalendar/daygrid'
    import timeGridPlugin from '@fullcalendar/timegrid'
    import interactionPlugin from '@fullcalendar/interaction'

    function formatEvent(event) {
        return {
            start: event.start,
            end: event.end,
            title: `${event.leader} (${event.location})`,
            display: 'block',
        };
    }

    export default {
        props: {
            events: [Object]
        },
        components: {
            FullCalendar // make the <FullCalendar> tag available
        },
        data() {
            return {
                calendarOptions: {
                    plugins: [ dayGridPlugin, timeGridPlugin, interactionPlugin ],
                    initialView: 'dayGridMonth',
                    headerToolbar: {
                        end: 'dayGridMonth timeGridWeek today prev,next',
                    },
                    allDaySlot: false,
                    slotMinTime: "05:00:00",
                    slotMaxTime: "22:00:00",

                    events: this.formatEvents(),
                }
            }
        },
        methods: {
            formatEvents() {
                return this.events.map(formatEvent);
            }
        }
    }
</script>
<template>
  <FullCalendar ref="calendar" :options="calendarOptions" />
</template>

<style>
    /* clear UU styling */

    table thead th {
        border-bottom: unset;
    }

    table tfoot th {
        border-top: unset;
    }

    table tbody tr:nth-of-type(odd) {
        background: unset;
    }

    table tbody tr:hover {
        background: unset;
    }

    table tbody tr.no-background:hover, table tbody tr.no-background {
        background: unset;
    }

    table tbody td, table thead th, table tfoot th {
        padding: unset;
    }
</style>
