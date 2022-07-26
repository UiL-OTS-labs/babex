<script lang="ts" setup>
    import {defineEmits, defineProps, ref} from 'vue';
    import {urls} from '../../urls';
    import {babexApi} from '../../api';

    import DateTimePicker from '../DateTimePicker.vue';

    let props = defineProps<{
        id?: string,
        start: Date,
        end: Date,
        locations: {id: number, name: string}[],
        comment?: string,
    }>();

    const emit = defineEmits(['done']);

    const formAction = urls.agenda.closing.add;
    let form = ref({
        start: props.start,
        end: props.end,
        is_global: true,
        location: null,
        comment: props.comment,
    });

    async function remove(id: number) {
        babexApi.agenda.closing.delete(id).then(() => {
            emit('done');
        });
    }

    function onSubmit(event) {
        let promise;

        if (props.id) {
            promise = babexApi.agenda.closing.update(props.id, form.value);
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
      <label><input v-model="form.is_global" type="radio" value="true" />Entire building</label>
      <label><input v-model="form.is_global" type="radio" value="false" />Location:</label>
      <select :disabled="form.is_global === 'true'" v-model="form.location">
        <option v-for="location in locations"
                :key="location.id" :value="location.id">{{ location.name }}</option>
      </select>
    </div>
    <div>
      <label>Comments:</label>
      <textarea v-model="form.comment"></textarea>
    </div>
    <div><button class="btn save">Save</button></div>
  </form>

  <div v-if="id">
    <button class="btn btn-danger" @click="remove(id)">Remove</button>
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
