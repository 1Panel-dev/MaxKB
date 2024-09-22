<template>
  <div ref="chartsRef" :style="style" v-resize="changeChartSize"></div>
</template>
<script lang="ts" setup>
import { onMounted, nextTick, watch, onBeforeUnmount, ref } from 'vue'
import * as echarts from 'echarts'
const props = defineProps({
  option: {
    type: String,
    required: true
  }
})
const chartsRef = ref()

const style = ref({
  height: '220px',
  width: '100%'
})

function initChart() {
  if (chartsRef.value) {
    let myChart = echarts?.getInstanceByDom(chartsRef.value)
    if (myChart === null || myChart === undefined) {
      myChart = echarts.init(chartsRef.value)
    }
    const option = JSON.parse(props.option)
    if (option.actionType === 'EVAL') {
      myChart.setOption(evalParseOption(option), true)
    } else {
      myChart.setOption(jsonParseOption(option), true)
    }
  }
}
function jsonParseOption(option: any) {
  if (option.style) {
    style.value = option.style
  }

  if (option.option) {
    // 渲染数据
    return option.option
  }
  return option
}
function evalParseOption(option_json: any) {
  let option = {}
  eval(option_json.option)
  return option
}

function changeChartSize() {
  echarts?.getInstanceByDom(chartsRef.value)?.resize()
}

watch(
  () => props.option,
  (val) => {
    if (val) {
      nextTick(() => {
        initChart()
      })
    }
  }
)

onMounted(() => {
  nextTick(() => {
    initChart()
  })
})

onBeforeUnmount(() => {
  echarts.getInstanceByDom(chartsRef.value)?.dispose()
})
</script>
<style lang="scss" scoped></style>
