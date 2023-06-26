<script lang="ts" setup>
    let props = defineProps<{
        id: number
    }>();

    function cancel() {
        if (confirm('Are you sure?')) {
            window.location.href = `/appointment/${props.id}/cancel/`;
        }
    }
</script>

<template>
    <button class="btn btn-danger" @click="cancel()">Cancel appointment</button>
</template>
