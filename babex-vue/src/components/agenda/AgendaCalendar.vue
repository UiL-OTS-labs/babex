<script lang="ts" setup>
    import FullCalendar from '@fullcalendar/vue3';
    import dayGridPlugin from '@fullcalendar/daygrid';
    import timeGridPlugin from '@fullcalendar/timegrid';
    import interactionPlugin from '@fullcalendar/interaction';
    import type {EventInput, EventContentArg, CalendarOptions, EventSourceApi} from '@fullcalendar/core';
    import {defineEmits, defineExpose, defineProps, ref} from 'vue';

    import {urls} from '../../urls';

    const props = defineProps<{
        // optional starting date of valid selection range (iso format)
        start?: string,
        // optional ending date of valid selection range (iso format)
        end?: string,
    }>();

    function formatAppointment(event: EventInput) : EventInput {
        return {
            id: event.id,
            start: event.start,
            end: event.end,
            title: event.participant,
            location: event.location,
            // extra field will be displayed in a separate line
            extra: `${event.location} (${event.leader})`,
            display: 'block',
            category: 'appointment',
            comment: event.comment,
            outcome: event.outcome,
            experiment: event.experiment
        };
    }

    function formatClosing(event: EventInput) : EventInput {
        return {
            original: event,
            id: event.id,
            start: event.start,
            end: event.end,
            title: 'Closed',
            extra: event.is_global ? 'Entire building' : event.location_name,
            display: 'block',
            category: 'closing',
            comment: event.comment
        };
    }


    const emit = defineEmits(['select', 'eventClick']);

    const calendar = ref<typeof FullCalendar|null>(null);

    const calendarOptions: CalendarOptions = {
        plugins: [ dayGridPlugin, timeGridPlugin, interactionPlugin ],
        initialView: 'dayGridMonth',
        headerToolbar: {
            end: 'dayGridMonth timeGridWeek today prev,next',
        },
        allDaySlot: false,
        slotMinTime: "05:00:00",
        slotMaxTime: "22:00:00",
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        },
        displayEventEnd: true,
        eventSources: [
            {
                url: urls.agenda.feed,
                eventDataTransform: formatAppointment
            },
            {
                url: urls.agenda.closing,
                eventDataTransform: formatClosing,
                color: 'gray'
            },
        ],
        eventContent: eventRender,
        selectable: true,
        select: (info) => emit('select', info),
        eventClick: (info) => emit('eventClick', info),

        events: [
            { start: props.start, end: props.end, display: 'inverse-background', color: 'gray' }
        ],
        selectConstraint: {
            start: props.start,
            end: props.end
        }
    };

    // override built-in template with multiline support and styling for canceled appointments
    function eventRender(arg: EventContentArg) {
        let className = arg.event.extendedProps.outcome && 'event-' + arg.event.extendedProps.outcome.toLowerCase();

        return {
            html: `<div class="fc-event-main-frame ${className}"><div class="fc-event-time">${arg.timeText}</div>
              <div class="fc-event-title-container">
                <div class="fc-event-title fc-sticky">${arg.event.title}</div>
              </div></div>
              <div>${arg.event.extendedProps.extra ?? ''}</div>`
        }
    }

    function refresh() {
        const calendarApi = calendar.value!.getApi();
        calendarApi.getEventSources().forEach((src: EventSourceApi) => src.refetch());
    }

    defineExpose({calendar, refresh});
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

    .fc-event {
        cursor: pointer;
    }

    .event-selected {
        background: #8ac4fd;
        border-color: #8ac4fd;
    }

    .event-canceled div, .event-canceled + div {
        text-decoration: line-through;
    }
</style>
