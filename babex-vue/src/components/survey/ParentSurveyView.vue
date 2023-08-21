<script lang="ts" setup>
    /*
       This component is a thin wrapper around SurveyView that includes the relevant api calls
       for submitting survey data to the server
    */
    import { ref } from 'vue';
    import { parentApi } from '../../api';
    import SurveyView from './SurveyView.vue'

    let props = defineProps<{
        definition: any,
        invite_id: number,
        response?: { data: any, completed?: string, page: number },
    }>();

    let survey = ref<typeof SurveyView|null>(null);

    async function save(data: any, page: number) {
        await parentApi.survey.response.create({
            invite: props.invite_id,
            data: data,
            final: false,
            page: page
        });
    }

    async function send(data: any) {
        await parentApi.survey.response.create({
            invite: props.invite_id,
            data: data,
            final: true
        });
        // TODO redirect after submission
    }
</script>

<template>
    <SurveyView ref="survey" :definition="definition" @save="save" @send="send" :initial="response" />
</template>

<style>
</style>
