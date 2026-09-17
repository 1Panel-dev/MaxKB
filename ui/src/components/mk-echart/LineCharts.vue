<script setup lang="ts">
import { computed } from 'vue'
import { use, type ComposeOption } from 'echarts/core'
import { LineChart, type LineSeriesOption } from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  TooltipComponent,
  type GridComponentOption,
  type LegendComponentOption,
  type TooltipComponentOption,
} from 'echarts/components'
import { numberFormat } from '@/utils/number'
import MkEchart from './index.vue'
import type { MkLineChartOption } from './types'

use([LineChart, GridComponent, LegendComponent, TooltipComponent])
defineOptions({ name: 'MkLineChart' })
const props = withDefaults(
  defineProps<{
    option: MkLineChartOption
    width?: string
    height?: string
    valueFormatter?: (value: number) => string
  }>(),
  { width: '100%', height: '200px', valueFormatter: numberFormat },
)
type LineOption = ComposeOption<LineSeriesOption | GridComponentOption | LegendComponentOption | TooltipComponentOption>

/* 折线图默认配置 */
const chartOption = computed<LineOption>(() => ({
  color: ['#5285FF', '#FFCF2F', '#7F3BF5', '#2CA91F', '#14C0FF'],
  tooltip: {
    trigger: 'axis',
    renderMode: 'richText',
    valueFormatter: (value) => (typeof value === 'number' ? props.valueFormatter(value) : String(value ?? '—')),
  },
  legend: {
    show: props.option.yData.length > 1,
    top: 4,
    right: 0,
    icon: 'circle',
    itemWidth: 8,
    itemHeight: 8,
    textStyle: { color: '#646A73' },
  },
  grid: { left: 12, right: 16, top: 56, bottom: 0, containLabel: true },
  xAxis: {
    type: 'category',
    data: props.option.xData,
    boundaryGap: false,
    axisLine: { lineStyle: { color: '#EFF0F1' } },
    axisTick: { show: false },
    axisLabel: { color: '#646A73', margin: 16 },
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#646A73', formatter: (value: number) => props.valueFormatter(value) },
    splitLine: { lineStyle: { color: '#EFF0F1' } },
  },
  series: props.option.yData.map(({ area = true, ...series }) => ({
    type: 'line',
    smooth: true,
    showSymbol: false,
    lineStyle: { width: 2 },
    ...(area ? { areaStyle: { opacity: 0.05 } } : {}),
    ...series,
  })),
}))
</script>
<template>
  <MkEchart :option="chartOption" :width="width" :height="height" />
</template>
