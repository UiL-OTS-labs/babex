<script lang="ts" setup>
    import FullCalendar from '@fullcalendar/vue3';
    import dayGridPlugin from '@fullcalendar/daygrid';
    import timeGridPlugin from '@fullcalendar/timegrid';
    import interactionPlugin from '@fullcalendar/interaction';
    import type {EventInput, EventContentArg} from '@fullcalendar/core';
    import {defineProps} from 'vue';

    interface Appointment {
        start: Date,
        end: Date,
        experiment: string,
        leader: string,
        participant: string,
        location: string
    }

    function formatEvent(event: Appointment) : EventInput {
        return {
            start: event.start,
            end: event.end,
            title: event.participant,
            // extra field will be displayed in a separate line
            extra: `${event.leader} (${event.location})`,
            display: 'block',
        };
    }

    const props = defineProps<{
        events: Appointment[]
    }>();

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
        events: formatEvents(),
        eventContent: eventRender,
    };

    function formatEvents(): EventInput[] {
        return props.events.map(formatEvent);
    }

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
