<!--
     This Date/time picker is quite barebones for now, but hopefully it can be improved in the future
-->

<script lang="ts" setup>
    import {defineProps, ref, watch} from 'vue';

    function formatDate(date: Date) : string {
        let options = {
            timeStyle: 'short',
            dateStyle: 'short'
        };
        let formatter = new Intl.DateTimeFormat('nl-NL', options);
        return formatter.format(date);
    }

    function serializeDate(date: Date) : string {
        return date.toISOString();
    }

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

    function onChange(event: any) {
        innerDate.value = parseDate(event.target.value)
    }

    let props = defineProps<{
        date: Date,
        name: string
    }>();

    let innerDate = ref(props.date);
    watch(() => props.date, (newDate) => {innerDate.value = newDate});

</script>

<template>
  <div>
    <input type="text" :value="formatDate(innerDate)" @change="onChange" />
    <input type="hidden" :name="name" :value="serializeDate(innerDate)"/>
  </div>
</template>

<style scoped>
    input {
        width: 100%;
    }
</style>
