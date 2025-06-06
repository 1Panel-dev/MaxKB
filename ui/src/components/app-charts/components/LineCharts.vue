<template>
  <div :id="id" ref="PieChartRef" :style="{ height: height, width: width }" />
</template>
<script lang="ts" setup>
import { onMounted, nextTick, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { numberFormat } from '@/utils/utils'
const props = defineProps({
  id: {
    type: String,
    default: 'lineChartId'
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '200px'
  },
  option: {
    type: Object,
    required: true
  } // option: { title , data }
})

const color = ['rgba(82, 133, 255, 1)', 'rgba(255, 207, 47, 1)']

const areaColor = ['rgba(82, 133, 255, 0.2)', 'rgba(255, 207, 47, 0.2)']

function initChart() {
  let myChart = echarts?.getInstanceByDom(document.getElementById(props.id)!)
  if (myChart === null || myChart === undefined) {
    myChart = echarts.init(document.getElementById(props.id))
  }
  const series: any = []
  if (props.option?.yData?.length) {
    props.option?.yData.forEach((item: any, index: number) => {
      series.push({
        itemStyle: {
          color: color[index]
        },
        areaStyle: item.area
          ? {
              color: areaColor[index]
            }
          : null,
        ...item
      })
    })
  }
  const option = {
    title: {
      text: props.option?.title,
      textStyle: {
        fontSize: '16px'
      }
    },
    tooltip: {
      trigger: 'axis',
      valueFormatter: (value: any) => numberFormat(value)
      // axisPointer: {
      //   type: 'cross',
      //   label: {
      //     backgroundColor: '#6a7985'
      //   }
      // }
    },
    legend: {
      right: 0,
      itemWidth: 8,
      textStyle: {
        color: '#646A73'
      },
      icon: 'circle'
    },
    grid: {
      left: '1%',
      right: '1%',
      bottom: '0',
      top: '18%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: props.option.xData
    },
    yAxis: {
      type: 'value',
      splitLine: {
        lineStyle: {
          color: '#EFF0F1'
        }
      },
      axisLabel: {
        formatter: (value: any) => {
          return numberFormat(value)
        }
      }
    },
    series: series
  }

  // 渲染数据
  myChart.setOption(option, true)
}

function changeChartSize() {
  echarts.getInstanceByDom(document.getElementById(props.id)!)?.resize()
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
    window.addEventListener('resize', changeChartSize)
  })
})

onBeforeUnmount(() => {
  echarts.getInstanceByDom(document.getElementById(props.id)!)?.dispose()
  window.removeEventListener('resize', changeChartSize)
})
</script>
<style lang="scss" scoped></style>
