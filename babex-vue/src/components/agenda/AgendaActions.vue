<script lang="ts" setup>
    import { _ } from '@/util';
    import { ActionContext } from '@/types';
    import AppointmentForm from './AppointmentForm.vue';
    import ClosingForm from './ClosingForm.vue';
    import {defineEmits, defineProps} from 'vue';

    defineProps<{
        context: ActionContext,
    }>();

    let canEditClosings = window.getUser().isSupport;

    defineEmits(['done']);
</script>

<template>
    <div v-if="context.type">
        <div v-if="canEditClosings && context.type=='event-select' && context.event?.extendedProps?.category == 'closing'" class="action-panel">
            <h5>{{ _('Edit closing') }}</h5>
            <ClosingForm :key="context.event.id" :event="context.event"  :locations="context.locations ?? []" @done="$emit('done')" />
        </div>
        <div v-if="context.type=='event-select' && context.event?.extendedProps?.category == 'appointment'" class="action-panel">
            <h5>{{ _('Edit appointment') }}</h5>
            <AppointmentForm :key="context.event.id" :event="context.event"  :locations="context.locations ?? []" @done="$emit('done')" />
        </div>
        <div v-if="canEditClosings && context.type=='date-range'" class="action-panel">
            <h5>{{ _('Add closing') }}</h5>
            <ClosingForm :key="Math.random()" :start="context.start" :end="context.end" :locations="context.locations ?? []" @done="$emit('done')"
                         :calendar="context.calendar" />
        </div>
    </div>
</template>
