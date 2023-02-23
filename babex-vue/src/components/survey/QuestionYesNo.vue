<script lang="ts" setup>
    import {defineProps} from 'vue';

    const props = defineProps<{
        id: string,
        yes: string,
        no: string
    }>();
</script>

<template>
    <div>
        <label><input type="radio">{{yes}}</label>
        <label><input type="radio">{{no}}</label>
    </div>
</template>

<style>
</style>
