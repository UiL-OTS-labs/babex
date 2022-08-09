<script lang="ts" setup>
    import {defineEmits, defineProps, onMounted, ref} from 'vue';
    import {babexApi} from '../../api';

    import DateTimePicker from '../DateTimePicker.vue';

    let props = defineProps<{
        start?: Date,
        end?: Date,
        locations: {id: number, name: string}[],
        event?: any
    }>();

    const emit = defineEmits(['done']);

    let form = ref({
        start: props.event ? props.event.start : props.start,
        end: props.event ? props.event.end : props.end,
        is_global: props.event ? props.event.extendedProps.original.is_global : true,
        location: props.event ? props.event.extendedProps.original.location : null,
        comment: props.event ? props.event.extendedProps.original.comment : null
    });

    async function remove(id: number) {
        babexApi.agenda.closing.delete(props.event.id).then(() => {
            emit('done');
        });
    }

    function onSubmit(event) {
        let promise;

        if (props.event) {
            promise = babexApi.agenda.closing.update(props.event.id, form.value);
        }
        else {
            promise = babexApi.agenda.closing.create(form.value);
        }

        promise.then(() => emit('done'));

        event.preventDefault();
        event.stopPropagation();
        return false;
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
    <div>
      <label>Comments:</label>
      <textarea class="form-control" v-model="form.comment"></textarea>
    </div>
    <div><button class="btn btn-primary save">Save</button></div>
  </form>

  <div v-if="event">
    <button class="btn btn-danger" @click="remove(event.id)">Remove</button>
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
