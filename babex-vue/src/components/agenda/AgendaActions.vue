<script lang="ts" setup>
    import {defineProps, ref} from 'vue';
    import {urls} from '../../urls';
    import ClosingForm from './ClosingForm.vue';

    interface ActionContext {
        type: string
    }

    interface DateRangeContext extends ActionContext {
        start: Date,
        end: Date
    }

    const props = defineProps<{
        context: ActionContext,
        csrf: string
    }>();

    const formAction = urls.agenda.closing;
    let isGlobal = ref('true');
</script>

<template>
  <div>
  <h3>Actions</h3>
  <div v-if="context.type=='event-select' && context.event.extendedProps.category == 'closing'" class="action-panel">
    <h5>Edit closing</h5>
    <ClosingForm :key="context.event.id" :id="context.event.id" :start="context.event.start" :end="context.event.end"
       :comment="context.event.extendedProps.comment" :locations="context.locations" :csrf="csrf" />
  </div>
  <div v-if="context.type=='date-range'" class="action-panel">
    <h5>Add closing</h5>
    <ClosingForm :start="context.start" :end="context.end" :locations="context.locations"
       :csrf="csrf" />
  </div>
  </div>
</template>

<style scoped>
    .action-panel {
        background: #eee;
        padding: 8px;

    }

</style>
