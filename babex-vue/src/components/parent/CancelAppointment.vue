<script lang="ts" setup>
    import { _, confirm } from '@/util';

    let props = defineProps<{
        id: number
    }>();

    async function cancel() {
        if (await confirm(_('Are you sure?'))) {
            window.location.href = `/appointment/${props.id}/cancel/`;
        }
    }
</script>

<template>
    <button class="btn btn-danger" @click="cancel()">{{ _('Cancel appointment') }}</button>
</template>
