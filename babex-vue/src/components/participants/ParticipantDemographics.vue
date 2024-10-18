<script setup>
    import * as d3 from 'd3';
    import { ref, onMounted, watch } from 'vue';
    import { babexApi } from '../../api';
    import { formatDateISO } from '../../util';
    import { _ } from '@/util';

    let date = ref(formatDateISO(new Date()));
    let loading = ref(true);
    let experiment = ref(null);
    let criteria = ref({
        dyslexia_yes: true,
        dyslexia_no: true,
        multilingual_yes: true,
        multilingual_no: true,
        premature_yes: true,
        premature_no: true,
    });

    defineProps(['experiments']);

    let request = null;

    function makeGraph(container) {
        let graph = d3.select(container);

        const margin = { left: 30, right: 30, bottom: 40, top: 20 };
        const width = 1024;
        const height = 400;

        request = babexApi.participants.demographics.get(new Date(date.value), criteria.value, experiment.value);
        request.success(data => {
            let svg = graph
                .append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("transform",
                      "translate(" + margin.left + "," + margin.top + ")");

            let histogram = [];
            let counter = {};
            data.all.forEach(d => {
                let m = d[0] * 12 + d[1];
                if (counter[m]) counter[m]++;
                else counter[m] = 1;
            });
            histogram = Object.keys(counter).map(key => { return {x0: parseInt(key, 10), length: counter[key]}; });

            let series = histogram;

            let minMonth = Math.min(...series.map(d => d.x0));
            let maxMonth = Math.max(...series.map(d => d.x0));

            let months = [];
            for (let i=minMonth; i<=maxMonth; i++) {
                months.push(i);
            }

            let x = d3.scaleBand()
                      .domain(months)
                      .range([margin.left*1.5, width - margin.right])
                      .paddingOuter(0.2)
                      .paddingInner(0.2);
            svg.append("g")
               .attr("transform", "translate(0," + (height - margin.bottom * 2) + ")")
               .call(d3.axisBottom(x));

            let y = d3.scaleLinear().range([height - margin.bottom * 2, 0]);
            let maxCount = Math.max(...series.map(bin => bin.length));
            y.domain([0, Math.max(1, Math.ceil(maxCount * 1.1))]);

            svg.append("g")
               .attr("transform", `translate(${margin.left*1.5}, 0)`)
               .call(d3.axisLeft(y));

            let selection = svg.selectAll("rect") .data(series).enter();

            selection
                .append("rect")
                .attr("class", "color0")
                .attr("x", d => x(d.x0))
                .attr("y", d => y(d.length))
                .attr("width", x.bandwidth())
                .attr("height", d => { return height - margin.bottom * 2 - y(d.length); });
            selection
                .append('text')
                .attr('class', 'tip')
                .attr('x', d => x(d.x0) + x.bandwidth()/2)
                .attr('y', d => y(d.length) - 4)
                .text(d => d.length)
                .style('opacity', d => d.length > 0 ? 1 : 0);

            svg.append('text')
               .attr("x", margin.left)
               .attr("y", height - margin.bottom)
               .text(_('Age in months*'));
            svg.append('text')
               .attr("x", -height/2)
               .attr("y", 0)
               .attr('transform', 'rotate(-90)')
               .attr('text-anchor', 'middle')
               .text(_('Number of participants'));

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

    watch([date, experiment, criteria], () => {
        request?.cancel();
        d3.select('.graph svg').remove();
        loading.value = true;
        makeGraph('.graph');
    }, {deep: true});
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
        <div class="col-3">
            <div>{{ _('Criteria:') }}</div>
            <div class="criteria">
                <div>
                    {{ _('Parent with Dyslexia') }}
                    <div class="float-end">
                        <label>
                            <input v-model="criteria.dyslexia_yes" type="checkbox">
                            {{ _('Yes') }}
                        </label>
                        <label>
                            <input v-model="criteria.dyslexia_no" type="checkbox">
                            {{ _('No') }}
                        </label>
                    </div>
                </div>
                <div>
                    {{ _('Multilingual') }}
                    <div class="float-end">
                        <label>
                            <input v-model="criteria.multilingual_yes" type="checkbox">
                            {{ _('Yes') }}
                        </label>
                        <label>
                            <input v-model="criteria.multilingual_no" type="checkbox">
                            {{ _('No') }}
                        </label>
                    </div>
                </div>
                <div>
                    {{ _('Premature') }}
                    <div class="float-end">
                        <label>
                            <input v-model="criteria.premature_yes" type="checkbox">
                            {{ _('Yes') }}
                        </label>
                        <label>
                            <input v-model="criteria.premature_no" type="checkbox">
                            {{ _('No') }}
                        </label>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <h4>{{ _('Participants per age') }}</h4>
    <div class="graph">
        <div v-if="loading" class="loading">
            <div class="spinner-border" role="status"></div>
        </div>
    </div>
    <div>{{ _('* 1 = 1;0 to 1;31') }}</div>
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

    .criteria {
        font-size: 14px;
        list-style: none;
        padding: 0;

        input[type="checkbox"] {
            margin-right: 5px;
            margin-left: 8px;
        }
    }


</style>
