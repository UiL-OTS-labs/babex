<script lang="ts" setup>
    import '@fullcalendar/core/vdom';
    import { _ } from '@/util';
    import FullCalendar from '@fullcalendar/vue3';
    import dayGridPlugin from '@fullcalendar/daygrid';
    import timeGridPlugin from '@fullcalendar/timegrid';
    import interactionPlugin from '@fullcalendar/interaction';
    import type { EventInput, EventContentArg, CalendarOptions } from '@fullcalendar/core';
    import nlLocale from '@fullcalendar/core/locales/nl';
    import { defineEmits, defineExpose, defineProps, ref } from 'vue';

    import DateTimePicker from '../DateTimePicker.vue';
    import { urls } from '../../urls';

    const props = defineProps<{
        // optional starting date of valid selection range (iso format)
        start?: string,
        // optional ending date of valid selection range (iso format)
        end?: string,
        // optional experiment id for limiting feeds
        experiment?: number,

        duration?: number,
    }>();


    // instead of directly using fullcalendar's url event source,
    // we manually load data using the fetch api and check for changes.
    // this lets us avoid re-rendering the agenda when there are no changes on the server.
    class Source {
        last: Array<any> | null;
        lastArgs: {start: string, end: string} | null;
        url: string;

        constructor(url: string) {
            this.url = url;
            this.last = null;
            this.lastArgs = null;
        }

        source() {
            return (info: any, success: any) => {
                let args = {start: info.startStr, end: info.endStr} as any;
                if (props.experiment) {
                    args.experiment = props.experiment;
                }

                fetch(
                    this.url + '?' + new URLSearchParams(args)
                ).then(async response => {
                    let skip = false;
                    let data = await response.json();
                    if (this.last != null && JSON.stringify(this.lastArgs) == JSON.stringify(args)) {
                        if (JSON.stringify(this.last) == JSON.stringify(data)) {
                            skip = true;
                        }
                    }

                    if (!skip) {
                        this.last = data;
                        this.lastArgs = args;
                        success(data);
                    }
                })
            };
        }

        reset() {
            this.last = null;
            this.lastArgs = null;
        }
    }

    // from https://stackoverflow.com/a/64090995
    function hsl2rgb(h: number, s: number, l: number): [number, number, number] {
        let a = s * Math.min(l, 1 - l);
        let f = (n: number) => {
            let k = (n + h / 30) % 12;
            return l - a * Math.max(Math.min(k-3, 9-k, 1), -1);
        };
        return [f(0), f(8), f(4)];
    }

    function rgb2hex(r: number, g:number, b:number) {
        return "#" + [r, g, b].map(x => Math.round(x * 255).toString(16).padStart(2, '0')).join('');
    }

    function eventColor(event: EventInput) {
        // javascript doesn't have a built-in way to manipulate Math.random()'s seed
        // nor a built-in hash function, so the code below is a very simple deterministic RNG
        // that is using the relevant experiment id to generate a hue value
        // cf. https://en.wikipedia.org/wiki/Linear_congruential_generator
        let r = 0;
        for(let i = 0; i < event.experiment.id; i++) {
            r = (r * 75 + 74) % 65537;
        }
        r /= 65536;
        return rgb2hex(...hsl2rgb(r * 360, 0.7, 0.5));
    }

    function formatAppointment(event: EventInput): EventInput | boolean {
        let icon = '';
        if (event.outcome == "COMPLETED") {
            icon = '<img src="/static/done.png">';
        }
        else if (event.outcome == "NOSHOW") {
            icon = '<img src="/static/noshow.png">';
        }
        else if (event.outcome == "EXCLUDED") {
            icon = '<img src="/static/excluded.png">';
        }
        else if (!showCanceled.value && event.outcome == 'CANCELED') {
            return false;
        }

        return {
            id: event.id,
            start: event.start,
            end: event.end,
            title: event.participant.name,
            location: event.location,
            // extra field will be displayed in a separate line
            extra: `${icon} ${event.location} (${event.leader.name})`,
            display: 'block',
            category: 'appointment',
            comment: event.comment,
            outcome: event.outcome,
            experiment: event.experiment,
            participant: event.participant,
            leader: event.leader,
            color: eventColor(event),
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
    const showCanceled = ref<boolean>(false);

    const eventSource = new Source(urls.agenda.feed);
    const closingSource = new Source(urls.agenda.closing);

    const calendarOptions: CalendarOptions = {
        height: 'auto',
        progressiveEventRendering: true,
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
        slotDuration: {minutes: 15},
        defaultTimedEventDuration: {minutes: props.duration},
        forceEventDuration: props.duration ? true : false,
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        },
        displayEventEnd: true,
        eventSources: [
            {
                events: eventSource.source(),
                // formatAppointment may return false, but the type signature of eventDataTransform doesn't like it
                eventDataTransform: formatAppointment as any,
            },
            {
                events: closingSource.source(),
                eventDataTransform: formatClosing,
                color: 'gray',
            }
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
            html: `<div class="fc-event-main-frame ${className}">
                        <div class="fc-event-time">${arg.timeText}</div>
                        <div class="fc-event-title-container">
                            <div class="fc-event-title fc-sticky">${arg.event.title}</div>
                            <div>${arg.event.extendedProps.extra ?? ''}</div>
                        </div>
                    </div>`
        }
    }

    function refresh() {
        const calendarApi = calendar.value!.getApi();
        eventSource.reset();
        calendarApi.refetchEvents();
    }

    defineExpose({ calendar, refresh });
</script>

<template>
    <FullCalendar ref="calendar" :options="calendarOptions" />
    <div class="mt-2">
        <label><input type="checkbox" v-model="showCanceled" @change="refresh()"> {{ _('Show canceled appointments') }}</label>
    </div>

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

    .fc-event-main-frame {
        flex-direction: column;
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
