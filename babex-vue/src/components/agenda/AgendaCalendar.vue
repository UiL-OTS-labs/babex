<script lang="ts" setup>
    import FullCalendar from '@fullcalendar/vue3';
    import dayGridPlugin from '@fullcalendar/daygrid';
    import timeGridPlugin from '@fullcalendar/timegrid';
    import interactionPlugin from '@fullcalendar/interaction';
    import type {EventInput, EventContentArg} from '@fullcalendar/core';
    import {defineEmits, defineExpose, ref} from 'vue';

    import {urls} from '../../urls';
    import type {Appointment, Closing} from '../../types';

    function formatAppointment(event: Appointment) : EventInput {
        return {
            id: event.id,
            start: event.start,
            end: event.end,
            title: event.participant,
            // extra field will be displayed in a separate line
            extra: `${event.location} (${event.leader})`,
            display: 'block',
            category: 'appointment'
        };
    }

    function formatClosing(event: Closing) : EventInput {
        return {
            original: event,
            id: event.id,
            start: event.start,
            end: event.end,
            title:'Closed',
            extra: event.is_global ? 'Entire building' : event.location_name,
            display: 'block',
            category: 'closing',
            comment: event.comment
        };
    }


    const emit = defineEmits(['select', 'eventClick']);

    let calendar = ref(null);

    const calendarOptions = {
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
        eventClick: (info) => emit('eventClick', info)
    };

    function eventRender(arg: EventContentArg) {
        // override built-in template with multiline support
        return {
            html: `<div class="fc-event-main-frame"><div class="fc-event-time">${arg.timeText}</div>
              <div class="fc-event-title-container">
                <div class="fc-event-title fc-sticky">${arg.event.title}</div>
              </div></div>
              <div>${arg.event.extendedProps.extra}</div>`
        }
    }

    function refresh() {
        let calendarApi = calendar.value.getApi();
        calendarApi.getEventSources().forEach((src) => src.refetch());
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
</style>
