<script lang="ts" setup>
    import {defineEmits, defineProps} from 'vue';
    import ClosingForm from './ClosingForm.vue';

    interface ActionContext {
        type: string
    }

    /*
    interface DateRangeContext extends ActionContext {
        start: Date,
        end: Date
    }
    */

    defineProps<{
        context: ActionContext,
    }>();

    defineEmits(['done']);
</script>

<template>
    <div v-if="context.type">
        <div v-if="context.type=='event-select' && context.event.extendedProps.category == 'closing'" class="action-panel">
            <h5>Edit closing</h5>
            <ClosingForm :key="context.event.id" :event="context.event"  :locations="context.locations" @done="$emit('done')" />
        </div>
        <div v-if="context.type=='date-range'" class="action-panel">
            <h5>Add closing</h5>
            <ClosingForm :key="Math.random()" :start="context.start" :end="context.end" :locations="context.locations" @done="$emit('done')" />
        </div>
    </div>
</template>

<style scoped>
</style>
