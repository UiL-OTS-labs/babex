<script lang="ts" setup>
    import {defineProps, reactive, watch} from 'vue';

    defineProps<{
        modelValue?: string[],
        options: string[],
        items: string[],
        radio: boolean,
    }>();

    const emit = defineEmits(['update:modelValue']);
    let choices = reactive([]);
    watch(choices, () => emit('update:modelValue', choices));
</script>

<template>
    <div>
        <table class="table">
            <tr>
                <th></th>
                <th v-for="option in options" :key="option">
                    {{option}}
                </th>
            </tr>
            <tr v-for="(item, index) in items" :key="index">
                <td>{{item}}</td>
                <th v-for="option in options" :key="option">
                    <input class="form-check-input" v-if="radio" :value="option" v-model="choices[index]" type="radio"/>
                    <input class="form-check-input" v-if="!radio" :value="option" v-model="choices[index]" type="checkbox"/>
                </th>
            </tr>
        </table>
    </div>
</template>

<style>
</style>
