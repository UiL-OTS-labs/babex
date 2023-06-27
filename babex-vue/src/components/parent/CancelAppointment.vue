<script lang="ts" setup>
    import { _ } from '@/util';

    let props = defineProps<{
        id: number
    }>();

    function cancel() {
        if (confirm(_('Are you sure?'))) {
            window.location.href = `/appointment/${props.id}/cancel/`;
        }
    }
</script>

<template>
    <button class="btn btn-danger" @click="cancel()">Cancel appointment</button>
</template>
