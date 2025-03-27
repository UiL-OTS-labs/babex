<script lang="ts" setup>
    import { _ } from '@/util';

    const props = defineProps<{
        message: string,
        ok?: string,
        cancel?: string,
    }>();

    let ok = props.ok ? props.ok : _("Ok");
    let cancel = props.cancel ? props.cancel : _("Cancel");

    defineEmits(['ok', 'cancel']);
</script>

<template>
    <Teleport to="body">
        <div id="modal-backdrop" class="modal-backdrop fade show" style="display:block;"></div>
        <div id="modal" class="modal fade show" tabindex="-1" style="display:block;">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-body">
                        {{ message }}
                    </div>
                    <div class="modal-footer">
                        <button @click="$emit('cancel')" type="button" class="btn btn-secondary">{{ cancel }}</button>
                        <button @click="$emit('ok')" type="button" class="btn btn-primary">{{ ok }}</button>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<style scoped>
</style>
