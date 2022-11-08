<script lang="ts" setup>
    import AgendaActions from './AgendaActions.vue';
    import AgendaCalendar from './AgendaCalendar.vue';
    import {ActionContext, Location} from '@/types';
    import {defineProps, ref} from 'vue';
    import { DateSelectArg, EventClickArg } from '@fullcalendar/common';

    const calendar = ref<typeof AgendaCalendar|null>(null);

    const props = defineProps<{
        locations: Location[],
    }>();

    const actionContext = ref<ActionContext>({});

    function deselectEvents() {
        document.querySelectorAll('.event-selected').forEach(
            (el) => {el.classList.remove('event-selected');}
        );
    }


    // Called when a day is selected.
    function onSelect(selectionInfo: DateSelectArg) {
        deselectEvents();
        actionContext.value = {
            type: 'date-range',
            start: selectionInfo.start,
            end: selectionInfo.end,
            locations: props.locations
        };
    }

    // Called when a specific event (appointment, closing, ...) is selected.
    function onEventClick(eventInfo: EventClickArg) {
        deselectEvents();
        const element = eventInfo.el;
        element.classList.add('event-selected');

        const event = eventInfo.event;
        actionContext.value = {
            type: 'event-select',
            event: event.toJSON(),
            locations: props.locations
        };
    }

    function actionDone() {
        calendar.value?.refresh();
        actionContext.value = {};
    }
</script>

<template>
  <div class="uu-sidebar-container uu-sidebar-right compact-sidebar">
    <aside class="uu-sidebar">
      <AgendaActions :context="actionContext" @done="actionDone" />
    </aside>
    <div class="uu-sidebar-content">
      <AgendaCalendar ref="calendar" @select="onSelect" @eventClick="onEventClick" />
    </div>
</div>
</template>

<style>
    .compact-sidebar {
        --bs-uu-sidebar-width: 250px;
        --bs-uu-sidebar-gap: 40px;
    }
</style>
