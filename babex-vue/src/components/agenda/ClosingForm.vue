<script lang="ts" setup>
    import {defineEmits, defineProps, ref, onUnmounted, watchEffect} from 'vue';
    import {babexApi} from '../../api';
    import {Location} from '@/types';
    import DateTimePicker from '../DateTimePicker.vue';
    import {EventApi} from '@fullcalendar/core';
    import AgendaCalendar from './AgendaCalendar.vue';

    const props = defineProps<{
        start?: Date,
        end?: Date,
        locations: Location[],
        // eslint-disable-next-line
        event?: any,
        calendar?: typeof AgendaCalendar,
    }>();

    const emit = defineEmits(['done']);

    const DAY = 24 * 3600 * 1000; // day span in milliseconds

    const form = ref({
        start: props.event ? props.event.start : props.start,
        end: props.event ? props.event.end : props.end,
        is_global: props.event ? props.event.extendedProps.original.is_global : true,
        location: props.event ? props.event.extendedProps.original.location : null,
        comment: props.event ? props.event.extendedProps.original.comment : null,
        repeat: false,
        repeatDays: 1
    });

    const temporaryEvents = ref<EventApi[]>([]);

    async function remove() {
        babexApi.agenda.closing.delete(props.event.id).then(() => {
            emit('done');
        });
    }

    function onSubmit(ev: Event) {
        let promise;

        if (props.event) {
            promise = babexApi.agenda.closing.update(props.event.id, form.value);
        }
        else {
            let closings = temporaryEvents.value.map((event) => {
                return {
                    start: event.start!,
                    end: event.end!,
                    is_global: form.value.is_global,
                    location: form.value.location,
                    comment: form.value.comment
                };
            });
            promise = babexApi.agenda.closing.createMany(closings);
        }

        promise.then(() => emit('done'));

        ev.preventDefault();
        ev.stopPropagation();
        return false;
    }

    if (!props.event) {
        // Interactively create temporary events in the calendar, to visually assist
        // with repeating closings. Only available when creating a new closing
        watchEffect(() => {
            temporaryEvents.value.forEach((event) => {
                event.remove();
            })
            temporaryEvents.value = [];
            let range = form.value.repeat ? form.value.repeatDays : 1;
            for(let i=0; i<range; i++) {
                let event = props.calendar?.calendar.getApi().addEvent({
                    start: new Date(form.value.start.getTime() + (DAY * i)),
                    end: new Date(form.value.end.getTime() + (DAY * i)),
                    category: 'closing',
                    display: 'block',
                    title: 'Closed',
                    extra: ''
                });
                temporaryEvents.value.push(event);
            }
        });

        onUnmounted(() => {
            temporaryEvents.value.forEach((event) => {
                event.remove();
            })
        });
    }

    function isRepeatAllowed() {
        // check if the selected range is less than 24 hours
        return (form.value.end.getTime() - form.value.start.getTime()) < DAY;
    }
</script>

<template>
  <form @submit="onSubmit">
    <div>From:</div>
    <DateTimePicker class="closing-start" v-model="form.start" />
    <div>To:</div>
    <DateTimePicker class="closing-end" v-model="form.end" />
    <div>
        <div class="form-check">
            <label><input class="form-check-input" v-model="form.is_global" type="radio" value="true" />Entire building</label>
        </div>
        <div class="form-check">
            <label><input class="form-check-input" v-model="form.is_global" type="radio" value="false" />Location:</label>
        </div>
        <select class="form-select" :disabled="form.is_global === true" v-model="form.location">
        <option v-for="location in locations"
                :key="location.id" :value="location.id">{{ location.name }}</option>
      </select>
    </div>
    <div v-if="!props.event && isRepeatAllowed()"> <!-- only available when creating a new closing -->
        <div class="form-check">
            <label>
                <input class="form-check-input" v-model="form.repeat" type="checkbox" value="false" />
                Repeat for
            </label>
            <input type="number" class="ms-2 repeat-days form-control" min="1" v-model="form.repeatDays"
                   :disabled="!form.repeat" /> days
        </div>
    </div>
    <div>
      <label>Comments:</label>
      <textarea class="form-control" v-model="form.comment"></textarea>
    </div>
    <div><button class="btn btn-primary save">Save</button></div>
  </form>

  <div v-if="event">
    <button class="btn btn-danger" @click="remove()">Remove</button>
  </div>
</template>

<style scoped>
    input[type="text"], select, textarea {
        width: 100%;
    }

    select {
        margin-bottom: 6px;
    }

    button {
        width: 100%;
        margin-top: 2px;
        margin-bottom: 4px;
    }

    .btn.save {
        margin-top: 6px;
    }

    .repeat-days {
        width: 8ex;
        display: inline;
    }
</style>
