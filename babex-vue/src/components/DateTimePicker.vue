<!--
     This Date/time picker is quite barebones for now, but hopefully it can be improved in the future
-->

<script lang="ts" setup>
    import {defineEmits, defineProps } from 'vue';
    import {formatDateTime} from '../util';

    function parseDate(dateStr: string) : Date {
        // unfortunately, the Intl date api doesn't provide a paring function,
        // so this is manually written to parse nl-NL date strings
        let parts = dateStr.split(' ');
        let datePart = parts[0];
        let timePart = parts[1];
        return new Date(
            datePart.split('-').reverse().join('-') + 'T' + timePart
        );
    }

    function onChange(event) {
        emits('update:modelValue', parseDate(event.target.value));
    }

    defineProps<{
        modelValue: Date,
    }>();

    const emits = defineEmits(['update:modelValue']);
</script>

<template>
  <div>
      <input class="form-control" type="text" :value="formatDateTime(modelValue)" @change="onChange">
  </div>
</template>

<style scoped>
    input {
        width: 100%;
    }
</style>
