<script lang="ts" setup>
    import '@fullcalendar/core/vdom';
    import { _ } from '@/util';
    import FullCalendar from '@fullcalendar/vue3';
    import dayGridPlugin from '@fullcalendar/daygrid';
    import timeGridPlugin from '@fullcalendar/timegrid';
    import interactionPlugin from '@fullcalendar/interaction';
    import type { EventInput, EventContentArg, CalendarOptions, EventSourceApi } from '@fullcalendar/core';
    import nlLocale from '@fullcalendar/core/locales/nl';
    import { defineEmits, defineExpose, defineProps, ref } from 'vue';

    import DateTimePicker from '../DateTimePicker.vue';
    import { urls } from '../../urls';

    const props = defineProps<{
        // optional starting date of valid selection range (iso format)
        start?: string,
        // optional ending date of valid selection range (iso format)
        end?: string,

        scheduling?: boolean,
    }>();

    function formatAppointment(event: EventInput): EventInput {
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

    function formatClosing(event: EventInput): EventInput {
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

    function showGoToDate() {
        goToModal.value = true;
    }

    function goToDate() {
        calendar.value?.calendar.gotoDate(date.value);
        goToModal.value = false;
    }


    const emit = defineEmits(['select', 'eventClick']);

    const calendar = ref<typeof FullCalendar | null>(null);
    const goToModal = ref<boolean>(false);
    const date = ref<Date>(new Date());

    const calendarOptions: CalendarOptions = {
        plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
        initialView: 'dayGridMonth',
        customButtons: {
            goto: {
                text: _('go to'),
                click: showGoToDate
            }
        },
        headerToolbar: {
            end: 'dayGridMonth timeGridWeek prev,today,next goto',
        },
        allDaySlot: false,
        slotMinTime: "07:00:00",
        slotMaxTime: "20:00:00",
        slotDuration: props.scheduling ? "00:15:00" : "00:30:00",
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
        },
        locale: window.getLanguage() == 'nl' ? nlLocale : undefined
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

    defineExpose({ calendar, refresh });
</script>

<template>
    <FullCalendar ref="calendar" :options="calendarOptions" />

    <Teleport to="body">
        <div v-if="goToModal">
            <div id="modal-backdrop" class="modal-backdrop fade show" style="display:block;"></div>
            <div id="modal" class="modal fade show" tabindex="-1" style="display:block;">
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div class="modal-content">
                        <div class="modal-body">
                            <form @submit="goToDate()">
                                <DateTimePicker :time="false" v-model="date"/>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button @click="goToDate()" type="button" class="btn btn-primary">{{ _('Confirm') }}</button>
                            <button @click="goToModal = false" type="button" class="btn btn-secondary">{{ _('Cancel')}}</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>

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

    table tbody tr.no-background:hover,
    table tbody tr.no-background {
        background: unset;
    }

    table tbody td,
    table thead th,
    table tfoot th {
        padding: unset;
    }

    .fc-event {
        cursor: pointer;
    }

    .event-selected {
        background: #8ac4fd;
        border-color: #8ac4fd;
    }

    .event-canceled div,
    .event-canceled+div {
        text-decoration: line-through;
    }
</style>
