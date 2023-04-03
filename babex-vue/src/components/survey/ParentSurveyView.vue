<script lang="ts" setup>
    /*
       This component is a thin wrapper around SurveyView that includes the relevant api calls
       for submitting survey data to the server
    */
    import {parentApi} from '../../api';
    import SurveyView from './SurveyView.vue'

    let props = defineProps<{
        definition: any
    }>();

async function send(data: any) {
        console.log(data);
        let result = await parentApi.survey.response.create({
            data: data
        });
        console.log(result);
    }
</script>

<template>
    <SurveyView :definition="definition" @send="send($event)"/>
</template>

<style>
</style>
