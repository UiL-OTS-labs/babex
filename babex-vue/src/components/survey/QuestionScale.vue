<script lang="ts" setup>
    import {defineProps, ref, watch} from 'vue';

    let props = defineProps<{
        modelValue?: string,
        options: string[],
    }>();

    const emit = defineEmits(['update:modelValue']);
    let choice = ref(props.modelValue);
    watch(choice, () => emit('update:modelValue', choice));
</script>

<template>
    <div>
        <div class="form-check form-check-inline" v-for="option in options" :key="option">
            <input class="form-check-input" type="radio" v-model="choice" :value="option">
            <label class="form-check-label"> {{option}} </label>
        </div>
    </div>
</template>

<style>
</style>
