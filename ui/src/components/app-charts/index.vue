<template>
  <component
    :is="typeComponentMap[type]"
    :height="height"
    :option="option"
    :dataZoom="dataZoom"
    class="v-charts"
  />
</template>
<script lang="ts" setup>
import line from './components/LineCharts.vue'
import bar from './components/BarCharts.vue'
defineOptions({ name: 'AppCharts' })
defineProps({
  type: {
    type: String,
    default: 'line',
  },
  height: {
    type: String,
    default: '200px',
  },
  dataZoom: Boolean,
  option: {
    type: Object,
    required: true,
  }, // { title , xData, yData, formatStr  }
})

const typeComponentMap = { line, bar } as any
</script>
