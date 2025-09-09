<template>
  <div class="charts-container">
    <div ref="chartsRef" :style="style" v-resize="changeChartSize"></div>
  </div>
</template>
<script lang="ts" setup>
import { onMounted, nextTick, watch, onBeforeUnmount, ref } from 'vue'
import * as echarts from 'echarts'
const tmp = ref()
const props = defineProps<{ option: string }>()
const chartsRef = ref()

const style = ref({
  height: '220px',
  width: '100%',
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
  if (option_json.style) {
    style.value = option_json.style
  }
  let option = {}
  tmp.value = echarts
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
  },
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
<style lang="scss" scoped>
.charts-container {
  overflow-x: auto;
}
.charts-container::-webkit-scrollbar-track-piece {
  background-color: rgba(0, 0, 0, 0);
  border-left: 1px solid rgba(0, 0, 0, 0);
}

.charts-container::-webkit-scrollbar {
  width: 5px;
  height: 5px;
  -webkit-border-radius: 5px;
  -moz-border-radius: 5px;
  border-radius: 5px;
}

.charts-container::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.5);

  background-clip: padding-box;

  -webkit-border-radius: 5px;

  -moz-border-radius: 5px;

  border-radius: 5px;

  min-height: 28px;
}

.charts-container::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.5);

  -webkit-border-radius: 5px;

  -moz-border-radius: 5px;

  border-radius: 5px;
}
</style>
