<script lang="ts" setup>
    import { defineProps, ref } from 'vue';
    import {formatDateTime} from '../util';

    interface UploadedFile {
        pk: number
        name: string,
        created: Date,
        link: string
    }

    const props = defineProps<{
        name: string
        existing: UploadedFile[]
    }>();

    const fields = ref([0]);
    const toRemove = ref(new Set());

    function add() {
        fields.value.push(fields.value.length);
    }

    function remove(index: number) {
        fields.value = fields.value.filter(x => x !== index);
    }

    function removeExisting(pk: number) {
        toRemove.value.add(pk);
    }

    function undoRemove(pk: number) {
        toRemove.value.delete(pk);
    }
</script>

<template>
    <div v-for="file in existing">
        <div class="existing-file">
            <div class="label" :class="{removed: toRemove.has(file.pk)}">
                <div><a :href="file.link">{{ file.name }}</a></div>
                <div>{{ formatDateTime(new Date(file.created)) }}</div>
            </div>
            <button v-if="toRemove.has(file.pk)" type="button" class="btn btn-secondary" @click="undoRemove(file.pk)">Cancel</button>
            <button v-if="!toRemove.has(file.pk)" type="button" class="btn btn-danger" @click="removeExisting(file.pk)">Remove</button>
        </div>
    </div>
    <div v-for="i in fields" :key="i">
        <div class="field">
            <input type="file" :name="name" class="form-control">
            <button type="button" class="btn btn-secondary" @click="remove(i)">Remove</button>
        </div>
    </div>

    <div>
        <button type="button" class="btn btn-secondary" @click="add()">+ add another</button>
    </div>

    <div v-for="entry in toRemove">
        <input type="hidden" :name="name + '_remove'" :value="entry">
    </div>
</template>

<style scoped>
    .existing-file {
        display: flex;
        margin-bottom: 5px;
    }

    .existing-file .label {
        display: flex;
        justify-content: space-between;
        padding: 5px;
        width: 100%;
        border: 1px solid #dedede;
        background: #dedede;
    }

    .field button, .existing-file button {
        margin-left: 5px;
        width: 20%;
    }

    .field {
        display: flex;
        margin-bottom: 5px;
    }

    input {
        margin-bottom: 5px;
    }

    .removed {
        text-decoration: line-through;
    }
</style>
