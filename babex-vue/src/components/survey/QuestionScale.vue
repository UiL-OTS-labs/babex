<script lang="ts" setup>
    import {defineProps, ref, watch} from 'vue';

    let props = defineProps<{
        modelValue?: string,
        options: string[],
    }>();

    const emit = defineEmits(['update:modelValue']);
    let choice = ref(props.modelValue);
    watch(choice, () => emit('update:modelValue', choice));
</script>

<template>
    <div>
        <table class="table">
            <tr>
                <td v-for="option in options" :key="option">
                    <label>
                        <input type="radio" v-model="choice" :value="option">
                        {{option}}
                    </label>
                </td>
            </tr>
        </table>
    </div>
</template>

<style>
</style>
