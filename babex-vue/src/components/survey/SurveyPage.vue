<script lang="ts" setup>
    import {reactive, watch} from 'vue';
    import {inject, Ref} from 'vue';
    import { Response } from '@/types';
    import QuestionYesNo from './QuestionYesNo.vue';
    import QuestionScale from './QuestionScale.vue';
    import QuestionMultiScale from './QuestionMultiScale.vue';
    import QuestionText from './QuestionText.vue';

    const props = defineProps<{
        definition: any,
        data?: any,
    }>();

    const emit = defineEmits(['ready']);

    const showErrors = inject('showErrors') as Ref<boolean>;
    let form = reactive<{ [id: string]: Response }>({});

    function questionId(idx: number) {
        return `q${idx}`;
    }

    function questionModel(index: number) {
        return form[questionId(index)];
    }

    function isReady() {
        return Object.values(form).every(response => !hasErrors(response));
    }

    function hasErrors(response: Response) {
        return response.question.required && (response.value === undefined || response.value!.length == 0)
    }

    watch(form, () => {
        if (isReady()) {
            // collect just the response values and propagate them upwards
            // we use the ?? operator to replace undefined with null, so that entries
            // are not removed from the object during serialization
            let collected = Object.fromEntries(Object.keys(form).map(key => [key, form[key].value ?? null]));
            emit('ready', true, collected);
        }
        else {
            emit('ready', false);
        }
    });
    props.definition.questions.forEach((question: any, idx: number) => {
        form[questionId(idx)] = { question: question, value: props.data?.[questionId(idx)] };
    });
</script>

<template>
    <div v-html="definition.intro">
    </div>
    <div class="card" v-for="(question, index) in definition.questions" :key="index">
        <div class="card-body">
            <div class="prompt" v-html="question.prompt"></div>
            <div class="question-body">
                <div v-if="question.template == 'yesno'">
                    <QuestionYesNo v-model="questionModel(index).value" yes="Yes" no="No"/>
                </div>
                <div v-if="question.template == 'text'">
                    <QuestionText v-model="questionModel(index).value" />
                </div>
                <div v-if="question.template == 'scale'">
                    <QuestionScale v-model="questionModel(index).value" :options="question.options" />
                </div>
                <div v-if="question.template == 'multi-scale'">
                    <QuestionMultiScale v-model="questionModel(index).value" :options="question.options" :items="question.items" :radio="question.radio" />
                </div>
            </div>
            <div v-if="showErrors && hasErrors(form[questionId(index)])" class="text-danger">please answer the question</div>
        </div>
    </div>
</template>

<style>
</style>
