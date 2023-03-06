<script lang="ts" setup>
    import {defineProps, ref} from 'vue';
    import QuestionYesNo from './QuestionYesNo.vue';
    import QuestionScale from './QuestionScale.vue';
    import QuestionText from './QuestionText.vue';

    const props = defineProps<{
        definition: any
    }>();

    interface Question {
        template: string,
        prompt: string,
    }

</script>

<template>
    <div class="card" v-for="(question, index) in definition.questions" :key="index">
        <div class="card-body">
            <div class="prompt">{{ question.prompt }}</div>
            <div class="question-body">
                <div v-if="question.template == 'yesno'">
                    <QuestionYesNo :id="'q'+index" yes="Yes" no="No" />
                </div>
                <div v-if="question.template == 'text'">
                    <QuestionText :id="'q'+index" />
                </div>
                <div v-if="question.template == 'scale'">
                    <QuestionScale :id="'q'+index" :options="question.options" />
                </div>
            </div>
        </div>
    </div>
</template>

<style>
</style>
