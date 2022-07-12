<script lang="ts" setup>
    import {defineProps, ref} from 'vue';
    import {urls} from '../../urls';

    import DateTimePicker from '../DateTimePicker.vue';

    let props = defineProps<{
        id?: string,
        start: Date,
        end: Date,
        locations: {id: number, name: string}[],
        comment: string,
        csrf: string
    }>();

    const formAction = urls.agenda.closing.add;
    let isGlobal = ref('true');
</script>

<template>
  <form :action="formAction" method="post">
    <div>From:</div>
    <DateTimePicker :date="start" name="start" />
    <div>To:</div>
    <DateTimePicker :date="end" name="end" />
    <div>
      <label><input v-model="isGlobal" type="radio" name="is_global" value="true" />Entire building</label>
      <label><input v-model="isGlobal" type="radio" name="is_global" value="false" />Location:</label>
      <select :disabled="isGlobal === 'true'" name="location">
        <option v-for="location in locations"
                :key="location.id" :value="location.id">{{ location.name }}</option>
      </select>
    </div>
    <div>
      <label>Comments:</label>
      <textarea name="comment">{{ comment }}</textarea>
    </div>
    <div><button class="btn save">Save</button></div>
    <input v-if="id" type="hidden" name="id" :value="id"/>
    <input type="hidden" name="csrfmiddlewaretoken" :value="csrf">
  </form>

  <form v-if="id" :action="urls.agenda.closing.delete" method="post">
    <button class="btn btn-danger">Remove</button>
    <input type="hidden" name="id" :value="id"/>
    <input type="hidden" name="csrfmiddlewaretoken" :value="csrf">
  </form>
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
