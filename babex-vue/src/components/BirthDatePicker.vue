<script lang="ts" setup>
    import { defineProps, computed, ref } from 'vue';

    const props = defineProps<{
        name: string, // form field name
        monthNames: string[],
        // getting date values from python, means they're strings
        value: string,
        minDate: string,
        maxDate: string
    }>();

    let days = [...Array(31).keys()].map(d => d + 1);
    let maxDateParsed = new Date(props.maxDate + 'T00:00');
    let minDateParsed = new Date(props.minDate + 'T00:00');
    let range = maxDateParsed.getFullYear() - minDateParsed.getFullYear();
    let years = [...Array(range + 1).keys()].map(y => y + minDateParsed.getFullYear());

    let year = ref('');
    let month = ref('');
    let day = ref('');

    if (props.value){
        let d = new Date(props.maxDate);
        year.value = d.getFullYear().toString();
        month.value = (d.getMonth() + 1).toString();
        day.value = d.getDate().toString();
    }
    const isValid = computed(() => {
        if (year.value && month.value && day.value) {
            let d = new Date(year.value, month.value - 1, day.value);
            return d >= minDateParsed && d < maxDateParsed;
        }
        return undefined;
    })
</script>

<template>
    <div class="d-flex">
        <select :id="'id_' + name + '_day'" class="form-control" :name="name + '_day'" v-model="day" :class="{'is-invalid': isValid === false}">

            <option value="">dag</option>
            <option v-for="day in days">
                {{ day }}
            </option>
        </select>
        <select :id="'id_' + name + '_month'" class="form-control" :name="name + '_month'" v-model="month" :class="{'is-invalid': isValid === false}">
            <option value="">maand</option>
            <option v-for="(month, index) in monthNames" :key="index" :value="index">
                {{ month }}
            </option>
        </select>
        <select :id="'id_' + name + '_year'" class="form-control" :name="name + '_year'" v-model="year" :class="{'is-invalid': isValid === false}">
            <option value="">jaar</option>
            <option v-for="year in years">{{ year }}</option>
        </select>
    </div>
</template>
