<script setup lang="ts" generic="T extends TableFilterValue = string[]">
import { computed } from 'vue'
import { cloneDeep } from 'lodash'
import type { CascaderOption, CascaderProps, CascaderValue } from 'element-plus'
import TableFilterSingle from './TableFilterSingle.vue'
import TableFilterMultiple from './TableFilterMultiple.vue'
import TableFilterCascader from './TableFilterCascader.vue'
import type { TableFilterOption, TableFilterValue } from './types'

defineOptions({ name: 'MkTableFilter' })

const props = withDefaults(
  defineProps<{
    label: string
    options: TableFilterOption[] | CascaderOption[]
    mode?: 'multiple' | 'single' | 'cascader'
    cascaderProps?: CascaderProps
    width?: string | number
  }>(),
  { mode: 'multiple' },
)
const emit = defineEmits<{ change: [value: T]; open: [] }>()
const selectedValue = defineModel<T>({ required: true })

// 统一筛选入口与提交，具体交互由模式组件维护。
const filterComponents = {
  single: TableFilterSingle,
  multiple: TableFilterMultiple,
  cascader: TableFilterCascader,
}
const hasSelection = computed(() =>
  Array.isArray(selectedValue.value)
    ? selectedValue.value.length > 0
    : selectedValue.value !== null && selectedValue.value !== undefined && selectedValue.value !== '',
)
const filterProps = computed(() => {
  if (props.mode === 'single') {
    return {
      modelValue: selectedValue.value as TableFilterOption['value'] | null | undefined,
      options: props.options as TableFilterOption[],
      active: hasSelection.value,
      width: props.width,
    }
  }
  if (props.mode === 'cascader') {
    return {
      modelValue: selectedValue.value as CascaderValue | null | undefined,
      options: props.options as CascaderOption[],
      cascaderProps: props.cascaderProps,
      width: props.width,
    }
  }
  return {
    modelValue: selectedValue.value as TableFilterOption['value'][],
    options: props.options as TableFilterOption[],
    width: props.width,
  }
})

function handleSelect(value: TableFilterValue) {
  const nextValue = cloneDeep(value) as T
  selectedValue.value = nextValue
  emit('change', nextValue)
}
</script>

<template>
  <component :is="filterComponents[mode]" v-bind="filterProps" @select="handleSelect" @open="emit('open')">
    <!-- 打开表头筛选 -->
    <el-button text>
      <span class="mr-1 font-semibold">{{ label }}</span>
      <MkIcon name="icon-filter" :class="hasSelection ? 'text-primary!' : 'text-N600'" />
    </el-button>
  </component>
</template>
