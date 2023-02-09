<script lang="ts" setup>
    import {defineEmits, defineProps, ref} from 'vue';
    import {babexApi} from '../../api';

    import DateTimePicker from '../DateTimePicker.vue';

    const props = defineProps<{
        locations: {id: number, name: string}[],
        // eslint-disable-next-line
        event: any,
        comment?: string,
    }>();

    const emit = defineEmits(['done']);


    const form = ref({
        start: props.event.start,
        end: props.event.end,
        participant: props.event.title,
        comment: props.event ? props.event.extendedProps.comment : null,
        location: props.event.extendedProps.location,
        outcome: props.event.extendedProps.outcome ?? undefined,
    });

    async function remove() {
        babexApi.agenda.appointment.delete(props.event.id).then(() => {
            emit('done');
        });
    }

    function onSubmit(event: Event) {
        let promise;

        if (isPast()) {
            // when the appointment is in the past, we only allow adding a comment and
            // setting the outcome value
            let update = {comment:form.value.comment, outcome: form.value.outcome};
            promise = babexApi.agenda.appointment.updatePartial(props.event.id, update);
        }
        else {
            promise = babexApi.agenda.appointment.update(props.event.id, form.value);
        }

        promise.then(() => emit('done'));

        event.preventDefault();
        event.stopPropagation();
        return false;
    }

    function isPast() {
        return props.event.start < (new Date());
    }

</script>

<template>
  <p><b>Participant:</b> {{form.participant}}</p>
  <form @submit="onSubmit">
    <div>From:</div>
    <DateTimePicker class="appointment-start" v-model="form.start" :readonly="isPast()" />

    <div>To:</div>
    <DateTimePicker class="appointment-end" v-model="form.end" :readonly="isPast()" />

    <div>
      <p><b>Location:</b> {{form.location}}</p>
    </div>

    <div>
      <label>Comments:</label>
      <textarea class="form-control" v-model="form.comment" :readonly="isPast()"></textarea>
    </div>
    <hr>

    <!-- only show outcome when the appointment (start time) is in the past -->
    <div v-if="isPast()">
        <div class="form-check">
            <label class="form-check-label"><input class="form-check-input" type="radio" value="COMPLETE" v-model="form.outcome">Complete</label>
        </div>
        <div class="form-check">
            <label class="form-check-label"><input class="form-check-input" type="radio" value="NOSHOW" v-model="form.outcome">No-show</label>
        </div>
        <div class="form-check">
            <label class="form-check-label"><input class="form-check-input" type="radio" value="EXCLUDED" v-model="form.outcome">Exclude</label>
        </div>
    </div>

    <div><button class="btn btn-primary save">Save</button></div>
  </form>

  <div v-if="!isPast()">
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
