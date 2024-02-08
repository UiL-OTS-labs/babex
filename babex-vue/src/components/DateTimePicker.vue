<!--
     This Date/time picker is quite barebones for now, but hopefully it can be improved in the future
-->

<script lang="ts" setup>
    import {defineEmits, defineProps } from 'vue';
    import {formatDateTime} from '../util';

    function parseDate(dateStr: string) : Date {
        // unfortunately, the Intl date api doesn't provide a paring function,
        // so this is manually written to parse nl-NL date strings
        const parts = dateStr.split(' ');
        const datePart = parts[0];
        const timePart = parts[1];
        return new Date(
            datePart.split('-').reverse().join('-') + 'T' + timePart
        );
    }

    function onChange(event: Event) {
        const element = event.target as HTMLInputElement;
        let date = parseDate(element.value);
        if (isFinite(Number(date))) {
            emits('update:modelValue', date);
        }
    }

    defineProps<{
        modelValue: Date,
        readonly?: boolean
    }>();

    const emits = defineEmits(['update:modelValue']);
</script>

<template>
  <div>
      <input :readonly="readonly" class="form-control" type="text" :value="formatDateTime(modelValue)" @change="onChange">
  </div>
</template>

<style scoped>
    input {
        width: 100%;
    }
</style>
