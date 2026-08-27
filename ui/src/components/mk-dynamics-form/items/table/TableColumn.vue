<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed } from 'vue'
const props = defineProps<{
  /**
   *表单渲染Item column
   */
  column: DynamicFormValue
  /**
   * 这一行数据
   */
  row: DynamicFormValue
}>()

const attrs = computed(() => {
  return props.column.attrs ? props.column.attrs : {}
})
</script>

<template>
  <component :is="column.property" v-bind="attrs" :column="column" :row="row"></component>
</template>
