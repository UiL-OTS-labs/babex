<script lang="ts" setup>
    import FullCalendar from '@fullcalendar/vue3';
    import dayGridPlugin from '@fullcalendar/daygrid';
    import timeGridPlugin from '@fullcalendar/timegrid';
    import interactionPlugin from '@fullcalendar/interaction';
    import type {EventInput, EventContentArg} from '@fullcalendar/core';
    import {defineProps, ref} from 'vue';

    import AgendaActions from './AgendaActions.vue';
    import {ActionContext} from './AgendaActions.vue';

    interface Appointment {
        start: Date,
        end: Date,
        experiment: string,
        leader: string,
        participant: string,
        location: string,
    }

    interface Closing {
        start: Date,
        end: Date,
        is_global: boolean,
        location: string,
        comment: string
    }

    interface Location {
        id: number,
        name: string
    }

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
            id: event.id,
            start: event.start,
            end: event.end,
            title:'Closed',
            extra: event.is_global ? 'Entire building' : event.location,
            display: 'block',
            category: 'closing',
            comment: event.comment
        };
    }

    const props = defineProps<{
        appointments: Appointment[],
        closings: Closing[],
        locations: Location[],
        csrf: string,
    }>();

    let actionContext = ref({});

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
        events: formatEvents(),
        eventContent: eventRender,
        selectable: true,
        select: onSelect,
        eventClick: onEventClick,
    };

    function formatEvents(): EventInput[] {
        return [].concat(
            props.appointments.map(formatAppointment),
            props.closings.map(formatClosing));

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

    function deselectEvents() {
        document.querySelectorAll('.event-selected').forEach(
            (el) => {el.classList.remove('event-selected');}
        );
    }

    function onSelect(selectionInfo) {
        deselectEvents();
        actionContext.value = {
            type: 'date-range',
            start: selectionInfo.start,
            end: selectionInfo.end,
            locations: props.locations
        };
    }

    function onEventClick(eventInfo) {
        deselectEvents();
        console.log(eventInfo);
        let element  = eventInfo.el;
        element.classList.add('event-selected');

        let event = eventInfo.event;
        actionContext.value = {
            type: 'event-select',
            event: event,
            locations: props.locations
        };
    }
</script>

<template>
  <div class="row">
    <div class="col-10">
      <FullCalendar ref="calendar" :options="calendarOptions" />
    </div>
    <div class="col-2">
      <AgendaActions :context="actionContext" :csrf="csrf" />
    </div>
  </div>
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
