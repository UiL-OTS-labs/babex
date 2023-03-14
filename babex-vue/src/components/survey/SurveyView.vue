<script lang="ts" setup>
    import {defineProps, provide, reactive, ref} from 'vue';
    import SurveyPage from './SurveyPage.vue';

    const props = defineProps<{
        definition: any
    }>();

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
        }
    }

    function prev() {
        if (currentPage.value > 0) {
            pageReady.value = false;
            currentPage.value--;
        }
    }

    function send() {
        // TODO
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
</script>

<template>
    <div>
        <SurveyPage :definition="definition.pages[currentPage]" :data="data[currentPage]"
                    @ready="onPageReady" :key="currentPage" />
    </div>
    <div class="mt-3">
        <button class="btn btn-secondary" @click="prev()" v-if="currentPage > 0">← Back</button>
        <button class="btn btn-primary float-end" @click="next()" v-if="!isLastPage()">Continue →</button>
        <button class="btn btn-primary float-end" @click="send()" v-if="isLastPage()">Send</button>
    </div>
</template>

<style>
</style>
