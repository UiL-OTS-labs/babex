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
    <div>
        <label><input type="radio" v-model="choice" :value="yes">{{yes}}</label>
        <label><input type="radio" v-model="choice" :value="no">{{no}}</label>
    </div>
</template>

<style>
</style>
