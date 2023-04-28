<script lang="ts" setup>
    import { defineEmits, ref, watch } from 'vue';

    const props = defineProps <{
        modelValue?: string,
    }>()

    const emit = defineEmits(['update:modelValue']);
    const text = ref(props.modelValue);

    watch(text, () => emit('update:modelValue', text));
</script>

<template>
    <div>
        <textarea class="form-control" v-model="text"></textarea>
    </div>
</template>

<style>
</style>
