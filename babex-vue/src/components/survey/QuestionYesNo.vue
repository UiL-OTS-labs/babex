<script lang="ts" setup>
    import { ref, watch } from 'vue';

    let props = defineProps<{
        modelValue?: string,
        yes: string,
        no: string,
    }>();

    let emit = defineEmits(['update:modelValue']);
    let choice = ref(props.modelValue);
    watch(choice, () => emit('update:modelValue', choice));
</script>

<template>
    <div class="form-check form-check-inline">
        <input type="radio" class="form-check-input" v-model="choice" :value="yes">
        <label class="form-check-label"> {{yes}} </label>
    </div>
    <div class="form-check form-check-inline">
        <input type="radio" class="form-check-input" v-model="choice" :value="no">
        <label class="form-check-label">{{no}}</label>
    </div>
</template>

<style>
</style>
