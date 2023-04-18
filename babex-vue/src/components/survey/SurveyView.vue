<script lang="ts" setup>
    import {defineProps, provide, reactive, ref} from 'vue';
    import SurveyPage from './SurveyPage.vue';

    const props = defineProps<{
        definition: any
    }>();

    const emit = defineEmits(['save', 'send']);

    let data = reactive([{}]);
    let currentPage = ref(0);

    let showErrors = ref(false);
    provide('showErrors', showErrors);
    let pageReady = ref(false);

    function next() {
        if (!pageReady.value) {
            showErrors.value = true;
            return;
        }

        if (currentPage.value < props.definition.pages.length - 1) {
            pageReady.value = false;
            currentPage.value++;
            emit('save', data, currentPage.value);
        }
    }

    function prev() {
        if (currentPage.value > 0) {
            pageReady.value = false;
            currentPage.value--;
        }
    }

    function send() {
        emit('send', data);
        // TODO redirect after submission
    }

    function save(pageIndex: number) {
        emit('save', data, pageIndex);
        // TODO redirect after submission
    }

    function isLastPage() {
        return currentPage.value == props.definition.pages.length - 1;
    }

    function onPageReady(isReady: boolean, formData: any) {
        pageReady.value = isReady;
        if (isReady) {
            data[currentPage.value] = formData;
        }
    }

    function restore(fromData: any, page: number) {
        currentPage.value = page;
        Object.assign(data, fromData);
    }

    defineExpose({ restore });
</script>

<template>
    <div>
        <SurveyPage :definition="definition.pages[currentPage]" :data="data[currentPage]"
                    @ready="onPageReady" :key="currentPage" />
    </div>
    <div class="mt-3">
        <button class="btn btn-secondary" @click="prev()" v-if="currentPage > 0">← Back</button>
        <div class="btn-group float-end">
            <button class="btn btn-secondary" @click="save(currentPage)" v-if="!isLastPage()">Save for later</button>
            <button class="btn btn-primary" @click="next()" v-if="!isLastPage()">Continue →</button>
            <button class="btn btn-primary" @click="send()" v-if="isLastPage()">Send</button>
        </div>
    </div>
</template>

<style>
</style>
