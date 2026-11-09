<template>
  <ProgressTableItem
    v-if="column.property === 'ProgressTableItem'"
    v-bind="attrs"
    :column="column"
    :row="row"
  />
</template>
<script setup lang="ts">
import { computed } from 'vue'
import ProgressTableItem from './ProgressTableItem.vue'
const props = defineProps<{
  /**
   *表单渲染Item column
   */
  column: any
  /**
   * 这一行数据
   */
  row: any
}>()

const attrs = computed(() => {
  const allowed = new Set([
    'color', 'stroke-width', 'text-inside', 'status', 'width', 'show-text', 'stroke-linecap',
    'type', 'indeterminate', 'duration', 'striped', 'striped-flow',
  ])
  return Object.fromEntries(Object.entries(props.column.attrs || {}).filter(([key]) => allowed.has(key)))
})
</script>
<style lang="scss" scoped></style>
