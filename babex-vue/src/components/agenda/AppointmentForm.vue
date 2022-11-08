<script lang="ts" setup>
    import {defineEmits, defineProps, ref} from 'vue';
    import {babexApi} from '../../api';

    import DateTimePicker from '../DateTimePicker.vue';

    const props = defineProps<{
        start?: Date,
        end?: Date,
        locations: {id: number, name: string}[],
        // eslint-disable-next-line
        event?: any,
        comment?: string
    }>();

    const emit = defineEmits(['done']);


    const form = ref({
        start: props.event ? props.event.start : props.start,
        end: props.event ? props.event.end : props.end,
        participant: props.event.title,
        comment: props.event ? props.event.extendedProps.comment : null,
        location: props.event.extendedProps.location,
    });

    async function remove() {
        babexApi.agenda.appointment.delete(props.event.id).then(() => {
            emit('done');
        });
    }

    function onSubmit(event: Event) {
        let promise;

        if (props.event) {
            promise = babexApi.agenda.appointment.update(props.event.id, form.value);
        }
        else {
            promise = babexApi.agenda.appointment.create(form.value);
        }

        promise.then(() => emit('done'));

        event.preventDefault();
        event.stopPropagation();
        return false;
    }

</script>

<template>
  <p><b>Participant:</b> {{form.participant}}</p>
  <form @submit="onSubmit">
    <div>From:</div>
    <DateTimePicker class="appointment-start" v-model="form.start" />

    <div>To:</div>
    <DateTimePicker class="appointment-end" v-model="form.end" />

    <div>
      <p><b>Location:</b> {{form.location}}</p>
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
</style>
