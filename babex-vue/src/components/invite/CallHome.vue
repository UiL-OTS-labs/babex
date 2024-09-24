<script lang="ts" setup>
    import { _ } from '@/util';
    import {defineProps, ref} from 'vue';
    import AgendaCalendar from '../agenda/AgendaCalendar.vue';
    import {babexApi} from '../../api';
    import {Call} from '../../types';
    import {EventApi, DateSelectArg} from '@fullcalendar/core';

    import DateTimePicker from '../DateTimePicker.vue';

    const props = defineProps<{
        participant: {id: number, name: string},
        experiment: {id: number, name: string},
        leaders: {id: number, name: string}[],
        statuses: { [id: string]: string},
        call: Call,
        completeUrl: string,

        // range during which the participant is eligible for participation in the experiment
        // passed from Django in an ISO-formatted string
        start: string,
        end: string
    }>();

    const calendar = ref<typeof AgendaCalendar|null>(null);
    const modalVisible = ref(false);
    const emailModalVisible = ref(false);
    const step = ref(0);
    const event = ref<EventApi|null>(null);
    const saving = ref(false);

    // event start and end times saved as separate refs because
    // our DateTimePicker doesn't play nicely with fullcalendar's event object
    const eventStart = ref<Date|null>(null);
    const eventEnd = ref<Date|null>(null);

    const callStatus = ref<string|null>(null);
    const comment = ref('');
    const confirmationForm = ref({
        leader: props.leaders[0].id,
        emailParticipant: true,
    });

    // we can probably skip type checking tinymce's interface
    type TinyMCE = any; // eslint-disable-line @typescript-eslint/no-explicit-any

    let emailEditor: TinyMCE;
    let appointment: number;
    let emailReady = false;

    function emailDialog() {
        modalVisible.value = false;
        emailModalVisible.value = true;
    }

    async function tinymcify(el: HTMLTextAreaElement) {
        emailEditor = (await window.tinymce.init({target: el, menubar: false}))[0];
        babexApi.call.appointment.getEmail(appointment).success(response => {
            emailEditor.setContent(response.content);
            emailReady = true;
        });
    }

    function confirmEmail() {
        // ignore send button clicked before email content was fetched
        if (!emailReady) return;

        babexApi.call.appointment.sendEmail({
            id: appointment,
            content: emailEditor.getContent()
        }).success(complete);
    }

    function confirm() {
        if(!event.value || !eventStart.value || !eventEnd.value) {
            return;
        }

        babexApi.call.appointment.create({
            start: eventStart.value,
            end: eventEnd.value,
            experiment: props.experiment.id,
            participant: props.participant.id,
            leader: confirmationForm.value.leader,
        }).success(response => {
            appointment = response.id!;
            if (confirmationForm.value.emailParticipant) {
                emailDialog();
            }
            else {
                complete();
            }
        });
    }

    function onSelect(selectionInfo: DateSelectArg) {
        if (selectionInfo.view.type === 'timeGridDay') {
            let now = new Date();
            if (selectionInfo.start < now) {
                // prevent selection in the past
                return;
            }

            if (event.value) {
                event.value.remove();
            }
            event.value = calendar.value?.calendar.getApi().addEvent({
                start: selectionInfo.start,
                end: selectionInfo.end
            });
            eventStart.value = selectionInfo.start;
            eventEnd.value = selectionInfo.end;
        }
        else {
            calendar.value?.calendar.getApi().changeView('timeGridDay', selectionInfo.start);
        }
    }

    function schedule() {
        step.value = 0;
        modalVisible.value = true;
        event.value = null;
    }

    function saveStatus() {
        if (callStatus.value == null || !props.call.id) {
            return;
        }

        saving.value = true;
        babexApi.call.log.update(props.call.id.toString(), {
            status: callStatus.value,
            comment: comment.value,
        }).success( () => {
            saving.value = false;
            complete();
        });
    }

    function cancel() {
        if (!props.call.id) {
            return;
        }

        saving.value = true;
        babexApi.call.log.update(props.call.id.toString(), {
            status: 'CANCELLED',
            comment: comment.value,
        }).success( () => {
            saving.value = false;
            complete();
        });
    }

    function complete() {
        location.href = props.completeUrl;
    }
</script>

<template>
    <div class="mb-5">
        <div class="btn-group">
            <button class="btn btn-primary" @click="schedule()">{{ _('Schedule appointment') }}</button>
        </div>
    </div>
    <div class="mb-3">
        {{ _('Alternative options:') }}
    </div>
    <div class="mb-3">
        <div class="form-check" v-for="(status, id) in statuses" :key="status">
            <input class="form-check-input" type="radio" :id="'status_'+id" :value="id" v-model="callStatus">
            <label class="form-check-label" :for="'status_'+id">{{status}}</label>
        </div>
    </div>
    <div class="mb-3">
        <label class="form-label">{{ _('Comments:') }}</label>
        <textarea class="form-control" v-model="comment"> </textarea>
    </div>
    <div class="mb-3">
        <button class="btn btn-primary" :class="{'btn-loading': saving}" @click="saveStatus" :disabled="callStatus==null">{{ _('Save') }}</button>
        <button class="btn btn-secondary m-3" :class="{'btn-loading': saving}" @click="cancel">{{ _('Cancel') }}</button>
    </div>

    <!-- dialog for picking appointment time and booking -->
    <Teleport to="body">
        <div v-if="modalVisible">
            <div id="modal-backdrop" class="modal-backdrop fade show" style="display:block;"></div>
            <div id="modal" class="modal fade show" tabindex="-1" style="display:block;">
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div v-if="step === 0" class="modal-content">
                        <div class="modal-body">
                            <AgendaCalendar ref="calendar" @select="onSelect" :start="start" :end="end" :scheduling="true"></AgendaCalendar>
                        </div>
                        <div class="modal-footer">
                            <button @click="step = 1" type="button" class="btn btn-primary" :disabled="event==null">{{ _('Next') }}</button>
                            <button @click="modalVisible = false" type="button" class="btn btn-secondary">{{ _('Cancel') }}</button>
                        </div>
                    </div>
                    <div v-if="step === 1 && eventStart && eventEnd" class="modal-content">
                        <div class="modal-body">
                            <h2>{{ _('Appointment details') }}</h2>
                            <table class="table mt-3">
                                <tr>
                                    <th>{{ _('Participant') }}</th><td>{{ participant.name }}</td>
                                </tr>
                                <tr>
                                    <th>{{ _('From') }}</th>
                                    <td><DateTimePicker v-model="eventStart" /></td>
                                </tr>
                                <tr>
                                    <th>{{ _('To') }}</th>
                                    <td><DateTimePicker v-model="eventEnd" /></td>
                                </tr>
                            </table>

                            <form>
                                <div class="row mb-3 justift-content-center">
                                    <label class="form-label">{{ _('Leader:') }}</label>
                                    <select class="form-select" v-model="confirmationForm.leader">
                                        <option v-for="leader in leaders" :value="leader.id" :key="leader.id">{{ leader.name }}</option>
                                    </select>
                                </div>
                                <div class="row mb-3 justift-content-center">
                                    <label class="form-label">
                                        <input class="me-2 form-check-input" type="checkbox"
                                               v-model="confirmationForm.emailParticipant"/>{{ _('Send confirmation email') }}
                                    </label>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button @click="confirm" type="button" class="btn btn-primary">{{ _('Confirm') }}</button>
                            <button @click="modalVisible = false" type="button" class="btn btn-secondary">{{ _('Cancel') }}</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>

    <!-- dialog for editing email before sending -->
    <Teleport to="body">
        <div v-if="emailModalVisible">
            <div id="modal-backdrop" class="modal-backdrop fade show" style="display:block;"></div>
            <div id="modal" class="modal fade show" tabindex="-1" style="display:block;">
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div class="modal-content">
                        <div class="modal-body">
                            <h2>{{ _('Review confirmation mail') }}</h2>
                            <textarea class="mail-preview" :ref="(el: any) => tinymcify(el as HTMLTextAreaElement)">
                            </textarea>
                        </div>
                        <div class="modal-footer">
                            <button @click="confirmEmail" type="button" class="btn btn-primary">{{ _('Send') }}</button>
                            <button @click="emailModalVisible = false" type="button" class="btn btn-secondary">{{ _('Cancel') }}</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<style scoped>
    textarea.mail-preview {
        height: 650px;
    }
</style>
