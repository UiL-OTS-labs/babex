<script lang="ts" setup>
    import {computed, defineEmits, defineProps, ref} from 'vue';
    import {babexApi} from '../../api';
    import {Location} from '../../types';
    import {formatDateTime} from '../../util';
    import { _ } from '@/util';

    import DateTimePicker from '../DateTimePicker.vue';

    const props = defineProps<{
        locations: Location[],
        // eslint-disable-next-line
        event: any,
        comment?: string,
    }>();

    const emit = defineEmits(['done']);


    const form = ref({
        start: props.event.start,
        comment: props.event ? props.event.extendedProps.comment : null,
        location: props.event.extendedProps.location,
        leader: props.event.extendedProps.leader,
        outcome: props.event.extendedProps.outcome ?? undefined,
    });

    async function cancel() {
        if (confirm(_('Are you sure?'))) {
            babexApi.agenda.appointment.delete(props.event.id).success(() => {
                emit('done');
            });
        }
    }

    function onSubmit(event: Event) {
        let promise;

        // when the appointment doesn't already have an outcome specified, we allow full modification.
        // otherwise, we only allow adding a comment or changing leader
        if (hasOutcome()) {
            let update = {comment:form.value.comment, leader: form.value.leader};
            promise = babexApi.agenda.appointment.updatePartial(props.event.id, update);
        }
        else {
            if (form.value.start - props.event.start != 0) {
                if (confirm(_('Move appointment to') + ' ' + formatDateTime(form.value.start) + '?')) {
                    promise = babexApi.agenda.appointment.updatePartial(props.event.id, form.value);
                }
            }
            else {
                promise = babexApi.agenda.appointment.updatePartial(props.event.id, form.value);
            }
        }

        if (promise) promise.success(() => emit('done'));

        event.preventDefault();
        event.stopPropagation();
        return false;
    }

    function hasOutcome() {
        return props.event.extendedProps.outcome;
    }

    function isPast() {
        return props.event.start < (new Date());
    }

    function isCanceled() {
        return props.event.extendedProps.outcome == 'CANCELED';
    }

    const eventEnd = computed(
        () => new Date(form.value!.start.getTime() + 60 * 1000 * props.event.extendedProps.experiment.session_duration));
</script>

<template>
    <div class="mt-4 mb-4">
        <div>
            <strong>{{ _('Participant:') }}</strong>
            <div>
                <a :href="'/participants/' + event.extendedProps.participant.id">
                    {{event.extendedProps.participant.name}}
                </a>
            </div>
        </div>
        <div>
            <strong>{{ _('Experiment:') }}</strong>&nbsp;
            <div>
                <a :href="'/experiments/' + event.extendedProps.experiment.id">
                    {{event.extendedProps.experiment.name}}
                </a>
            </div>
        </div>
        <div>
            <strong>{{ _('Location:') }}</strong>
            <div>{{form.location}}</div>
        </div>
        <div>
            <strong>{{ _('Leader:') }}</strong>
            <select class="form-select" v-model="form.leader">
            <option v-for="leader in event.extendedProps.experiment.leaders"
                :key="leader.id" :value="leader">{{ leader.name }}</option>
            </select>
        </div>
    </div>
    <form @submit="onSubmit">
        <div>{{ _('From:') }}</div>
        <DateTimePicker class="appointment-start" v-model="form.start" :readonly="hasOutcome()" />

        <div>{{ _('To:') }}</div>
        <DateTimePicker class="appointment-end" v-model="eventEnd" :readonly="true" />

        <div>
            <label>{{ _('Comments:') }}</label>
            <textarea class="form-control" v-model="form.comment"></textarea>
        </div>

        <!-- only show outcome when the appointment (start time) is in the past -->
        <div v-if="isPast() && !isCanceled()" class="mt-4">
            <div class="form-check">
                <label class="form-check-label"><input class="form-check-input" type="radio" value="COMPLETED" v-model="form.outcome" :disabled="hasOutcome()">{{ _('Complete') }}</label>
            </div>
            <div class="form-check">
                <label class="form-check-label"><input class="form-check-input" type="radio" value="NOSHOW" v-model="form.outcome" :disabled="hasOutcome()">{{ _('No-show') }}</label>
            </div>
            <div class="form-check">
                <label class="form-check-label"><input class="form-check-input" type="radio" value="EXCLUDED" v-model="form.outcome" :disabled="hasOutcome()">{{ _('Exclude') }}</label>
            </div>
        </div>

        <div class="mt-4"><button class="btn btn-primary save">{{ _('Save') }}</button></div>
    </form>

    <div v-if="!isPast() && !isCanceled()">
        <button class="btn btn-danger" @click="cancel()">{{ _('Cancel appointment') }}</button>
    </div>
</template>

<style scoped>
    input[type="text"], select, textarea {
        width: 100%;
    }

    select {
        margin-bottom: 6px;
    }

    button {
        width: 100%;
        margin-top: 2px;
        margin-bottom: 4px;
    }

    .btn.save {
        margin-top: 6px;
    }
</style>
