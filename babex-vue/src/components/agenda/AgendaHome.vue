<script lang="ts" setup>
    import AgendaActions from './AgendaActions.vue';
    import AgendaCalendar from './AgendaCalendar.vue';
    import {defineProps, ref} from 'vue';

    let calendar = ref(null);

    const props = defineProps<{
        locations: Location[],
    }>();

    let actionContext = ref({});

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
        let element = eventInfo.el;
        element.classList.add('event-selected');

        let event = eventInfo.event;
        actionContext.value = {
            type: 'event-select',
            event: event,
            locations: props.locations
        };
    }

    function actionDone() {
        calendar.value.refresh();
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
