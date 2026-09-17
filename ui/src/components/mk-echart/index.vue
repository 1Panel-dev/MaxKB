<script setup lang="ts">
import { onBeforeUnmount, onMounted, useTemplateRef, watch } from 'vue'
import { init, use, type EChartsCoreOption, type EChartsType } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'

use([CanvasRenderer])
defineOptions({ name: 'MkEchart' })
const props = withDefaults(
  defineProps<{
    option: EChartsCoreOption
    width?: string
    height?: string
  }>(),
  { width: '100%', height: '200px' },
)

/* 图表实例与容器尺寸 */
const container = useTemplateRef<HTMLDivElement>('container')
let chart: EChartsType | undefined
let resizeObserver: ResizeObserver | undefined
function renderChart() {
  if (!container.value?.clientWidth || !container.value.clientHeight) return
  if (!chart) chart = init(container.value)
  chart.setOption(props.option, { notMerge: true })
}
function resize() {
  if (!chart) renderChart()
  else chart.resize()
}
onMounted(() => {
  renderChart()
  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(container.value!)
})
watch(() => props.option, renderChart, { deep: true, flush: 'post' })
onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
  chart = undefined
})
defineExpose({ resize })
</script>
<template>
  <div ref="container" :style="{ width, height }" />
</template>
