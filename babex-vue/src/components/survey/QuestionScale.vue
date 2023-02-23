<script lang="ts" setup>
    import {defineProps} from 'vue';

    const props = defineProps<{
        id: string,
        options: string[],
    }>();
</script>

<template>
    <div>
        <table>
            <tr>
                <td v-for="option in options">
                    <label>
                    <input type="radio" :name="id">
                    {{option}}
                    </label>
                </td>
            </tr>
        </table>
    </div>
</template>

<style>
</style>
