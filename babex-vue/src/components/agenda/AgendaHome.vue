<script lang="ts" setup>
    import AgendaActions from './AgendaActions.vue';
    import AgendaCalendar from './AgendaCalendar.vue';
    import {ActionContext} from './AgendaActions.vue';
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
  <div class="uu-inner-container row">
    <div class="col-10 gx-4">
      <AgendaCalendar ref="calendar" @select="onSelect" @eventClick="onEventClick" />
    </div>
    <div class="col-2 gx-4">
      <AgendaActions :context="actionContext" @done="actionDone" />
    </div>
  </div>
</template>

<style>
</style>
