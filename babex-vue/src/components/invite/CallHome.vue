<script lang="ts" setup>
    import {defineProps, onMounted, ref} from 'vue';
    import AgendaCalendar from '../agenda/AgendaCalendar.vue';
    import {babexApi} from '../../api';
    import {Call} from '../../types';
    import {formatDate, formatTime} from '../../util';

    let props = defineProps<{
        participant: {id: number, name: string},
        experiment: {id: number, name: string},
        leaders: string[],
        statuses: { [id: string]: string},
        call: Call,
        completeUrl: string
    }>();

    let calendar = ref(null);
    let modalVisible = ref(false);
    let step = ref(0);
    let event = ref(null);
    let saving = ref(false);

    let callStatus = ref(null);
    let comment = ref('');
    let confirmationForm = ref({
        leader: props.leaders[0].id,
        emailParticipant: true,
    });

    function confirm() {
        babexApi.call.appointment.create({
            start: event.value.start,
            end: event.value.end,
            experiment: props.experiment.id,
            participant: props.participant.id,
            leader: confirmationForm.value.leader,
            emailParticipant: confirmationForm.value.emailParticipant
        }).then( () => {
            complete();
        });
    }

    function onSelect(selectionInfo) {
        if (selectionInfo.view.type === 'timeGridDay') {
            if (event.value) {
                event.value.remove();
            }
            event.value = calendar.value.calendar.getApi().addEvent({
                start: selectionInfo.start,
                end: selectionInfo.end
            });
        }
        else {
            calendar.value.calendar.getApi().changeView('timeGridDay', selectionInfo.start);
        }
    }

    function schedule() {
        step.value = 0;
        modalVisible.value = true;
        event.value = null;
    }

    function saveStatus() {
        saving.value = true;
        babexApi.call.log.update(props.call.id, {
            status: callStatus.value,
            comment: comment.value,
        }).then( () => {
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
            <button class="btn btn-primary" @click="schedule()">Schedule appointment</button>
        </div>
    </div>
    <div class="mb-3">
        Alternative options:
    </div>
    <div class="mb-3">
        <div class="form-check" v-for="(status, id) in statuses" :key="status">
            <input class="form-check-input" type="radio" :id="'status_'+id" :value="id" v-model="callStatus">
            <label class="form-check-label" :for="'status_'+id">{{status}}</label>
        </div>
    </div>
    <div class="mb-3">
        <label class="form-label">Comments:</label>
        <textarea class="form-control" v-model="comment"> </textarea>
    </div>
    <div class="mb-3">
        <button class="btn btn-primary" :class="{'btn-loading': saving}" @click="saveStatus">Save</button>
    </div>

    <Teleport to="body">
        <div v-if="modalVisible">
            <div id="modal-backdrop" class="modal-backdrop fade show" style="display:block;"></div>
            <div id="modal" class="modal fade show" tabindex="-1" style="display:block;">
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div v-if="step === 0" class="modal-content">
                        <div class="modal-body">
                                <AgendaCalendar ref="calendar" @select="onSelect"></AgendaCalendar>
                        </div>
                        <div class="modal-footer">
                            <button @click="step = 1" type="button" class="btn btn-primary" :disabled="event==null">Next</button>
                            <button @click="modalVisible = false" type="button" class="btn btn-secondary">Cancel</button>
                        </div>
                    </div>
                    <div v-if="step === 1" class="modal-content">
                        <div class="modal-body">
                            <h2>Appointment details</h2>
                            <table class="table mt-3">
                                <tr>
                                    <th>Participant</th><td>{{ participant.name }}</td>
                                </tr>
                                <tr>
                                    <th>Date</th><td>{{ formatDate(event.start) }}</td>
                                </tr>
                                <tr>
                                    <th>From</th>
                                    <td>{{ formatTime(event.start) }}</td>
                                </tr>
                                <tr>
                                    <th>To</th>
                                    <td>{{ formatTime(event.end) }}</td>
                                </tr>
                            </table>

                            <form>
                                <div class="row mb-3 justift-content-center">
                                    <label class="form-label">Leader:</label>
                                    <select class="form-select" v-model="confirmationForm.leader">
                                        <option v-for="leader in leaders" :value="leader.id" :key="leader.id">{{ leader.name }}</option>
                                    </select>
                                </div>
                                <div class="row mb-3 justift-content-center">
                                    <label class="form-label">
                                        <input class="me-2 form-check-input" type="checkbox"
                                               v-model="confirmationForm.emailParticipant"/>Send confirmation email
                                    </label>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button @click="confirm" type="button" class="btn btn-primary">Confirm</button>
                            <button @click="modalVisible = false" type="button" class="btn btn-secondary">Cancel</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<style scoped>
</style>
