<script lang="ts" setup>
    import { defineProps, ref } from 'vue';
    import {formatDateTime} from '../util';
    import { _ } from '@/util';

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
    const toRemove = ref<Set<number>>(new Set());

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
    <div v-for="file in existing" :key="file.pk">
        <div class="existing-file input-group">
            <div class="input-group-text flex-grow-1 justify-content-between" :class="{'text-decoration-line-through': toRemove.has(file.pk)}">
                <div><a :href="file.link"><span class="icon-file-text2">&#xe926;</span>{{ file.name }}</a></div>
                <div>{{ formatDateTime(new Date(file.created)) }}</div>
            </div>
            <button v-if="toRemove.has(file.pk)" type="button" class="btn btn-secondary" @click="undoRemove(file.pk)">{{ _('Cancel') }}</button>
            <button v-if="!toRemove.has(file.pk)" type="button" class="btn btn-danger" @click="removeExisting(file.pk)">{{ _('Remove') }}</button>
        </div>
    </div>
    <div v-for="i in fields" :key="i" class="mb-2">
        <div class="input-group">
            <input type="file" :name="name" class="form-control">
            <button type="button" class="btn btn-danger" @click="remove(i)">{{ _('Remove') }}</button>
        </div>
    </div>

    <div>
        <button type="button" class="btn btn-secondary" @click="add()">{{ _('+ add another') }}</button>
    </div>

    <div v-for="entry in toRemove" :key="entry">
        <input type="hidden" :name="name + '_remove'" :value="entry">
    </div>
</template>

<style scoped>
    .existing-file a {
        text-decoration: none;
    }

    .existing-file a span {
        padding-right: .3125rem;
    }
</style>
