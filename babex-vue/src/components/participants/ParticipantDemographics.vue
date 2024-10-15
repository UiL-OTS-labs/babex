<script setup>
    import * as d3 from 'd3';
    import { ref, onMounted, watch } from 'vue';
    import { babexApi } from '../../api';
    import { formatDateISO } from '../../util';
    import { _ } from '@/util';

    let date = ref(formatDateISO(new Date()));
    let loading = ref(true);
    let experiment = ref(null);
    let group = ref(null);

    let props = defineProps(['experiments']);

    let request = null;

    function makeGraph(container) {
        let graph = d3.select(container);

        const margin = { left: 30, right: 10, bottom: 40, top: 20 };
        const width = 1024;
        const height = 400;

        request = babexApi.participants.demographics.get(new Date(date.value), experiment.value);
        request.success(data => {
            let svg = graph
                .append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("transform",
                      "translate(" + margin.left + "," + margin.top + ")");

            let minMonth = 0;
            let maxMonth = 30;
            if (experiment.value) {
                // unlikely, but it could be that the experiment doesn't have set limits
                maxMonth = props.experiments[experiment.value].max_months || 30;
            }

            let x = d3.scaleLinear()
                      .domain([minMonth, maxMonth])
                      .range([0, width]);
            svg.append("g")
               .attr("transform", "translate(0," + (height - margin.bottom) + ")")
               .call(d3.axisBottom(x));

            let histogram = d3.bin()
                              .value(d => { return d[0] * 12 + d[1]; })
                              .domain(x.domain())
                              .thresholds(x.ticks(30));

            let groups = [];
            let series = {};

            if (group.value) {
                groups = Object.entries(data[group.value]);
            }
            else {
                groups = [['All', data.all]];
            }
            groups.forEach(([key, value]) => {
                series[key] = histogram(value);
            });


            let y = d3.scaleLinear().range([height - margin.bottom, 0]);
            let maxCount = 0;
            Object.values(series).forEach(bins => {
                maxCount = Math.max(maxCount, Math.max(...bins.map(bin => bin.length)));
            });
            y.domain([0, Math.max(1, Math.ceil(maxCount * 1.1))]);

            svg.append("g")
               .call(d3.axisLeft(y));

            let barWidth = (d)=> (x(d.x1) - x(d.x0))/groups.length - 4;

            Object.values(series).forEach((value, idx) => {
                svg.selectAll("rect" + idx)
                   .data(value)
                   .enter()
                   .append("rect")
                   .attr("class", "color" + idx)
                   .attr("x", d => barWidth(d) * idx + x(d.x0))
                   .attr("y", d => y(d.length))
                   .attr("width", barWidth)
                   .attr("height", d => { return height - margin.bottom - y(d.length); });

                svg.selectAll("text" + idx)
                   .data(value)
                   .enter()
                   .append('text')
                   .attr('class', 'tip')
                   .attr('x', d => barWidth(d) * idx + x(d.x0) + barWidth(d)/2)
                   .attr('y', d => y(d.length) - 4)
                   .text(d => d.length)
                   .style('opacity', d => d.length > 0 ? 1 : 0);

            });

            if (groups.length > 1) {
                svg.selectAll('legend')
                   .data(groups)
                   .enter()
                   .append('circle')
                   .attr('cx', width - 100)
                   .attr('cy', (_, i) => 30 * i)
                   .attr('r', 5)
                   .attr('class', (_, i) => 'color' + i);
                svg.selectAll('legendLabels')
                   .data(groups)
                   .enter()
                   .append('text')
                   .attr('x', width - 100 + 10)
                   .attr('y', (_, i) => 30 * i + 5)
                   .text(d => d[0]);
            }

            loading.value = false;
        });
        request.error((e) => {
            if (e.name != 'AbortError') {
                throw e;
            }
        });
    }

    onMounted(() => {
        makeGraph('.graph');
    })

    watch([date, experiment, group], () => {
        request?.cancel();
        d3.select('.graph svg').remove();
        loading.value = true;
        makeGraph('.graph');
    });
</script>

<template>
    <div class="row g-3 mb-5">
        <div class="col-2">
            <div class="m-1">{{ _('Show age on:') }}</div>
            <input type="date" class="form-control" v-model="date">
        </div>
        <div class="col-6">
            <div class="m-1">{{ _('Filter by experiment:') }}</div>
            <select class="form-control experiments" v-model="experiment">
                <option :value="null">---</option>
                <option v-for="e in experiments" :key="e.pk" :value="e.pk">{{ e.name }}</option>
            </select>
        </div>
        <div class="col-2">
            <div class="m-1">{{ _('Group by:') }}</div>
            <select class="form-control experiments" v-model="group">
                <option :value="null">---</option>
                <option value="dyslexia">{{ _('Parent with Dyslexia') }}</option>
                <option value="multilingual">{{ _('Multilingual') }}</option>
                <option value="premature">{{ _('Premature') }}</option>
            </select>
        </div>
    </div>
    <h4>{{ _('Participants per age (in months)') }}</h4>
    <div class="graph">
        <div v-if="loading" class="loading">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">{{ _('Loading...') }}</span>
            </div>
        </div>
    </div>
</template>

<style>
    .graph {
        width: 1024px;
        height: 400px;
    }

    .loading {
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    text.tip {
        font-size: 12px;
        fill: #000;
        text-anchor: middle;
    }

    .color0 {
        fill: #95d7ff;
    }

    .color1 {
        fill: #ff85be;
    }

</style>
