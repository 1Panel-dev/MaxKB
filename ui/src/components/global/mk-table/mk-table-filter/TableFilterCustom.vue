<script setup lang="ts">
import { ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { TableFilterCustomValue } from './types'

defineOptions({ name: 'TableFilterCustom' })
const props = defineProps<{
  modelValue: TableFilterCustomValue
  resetValue: TableFilterCustomValue
  width?: string | number
}>()

const emit = defineEmits<{ select: [value: TableFilterCustomValue]; open: [] }>()
defineSlots<{ default(): unknown; content(props: { value: TableFilterCustomValue }): unknown }>()

// 插槽只编辑独立草稿，确认或重置才回写已生效的筛选。
const visible = ref(false)
const pendingValue = ref<TableFilterCustomValue>(cloneDeep(props.modelValue))

function handleOpen() {
  pendingValue.value = cloneDeep(props.modelValue)
  emit('open')
}

function handleReset() {
  pendingValue.value = cloneDeep(props.resetValue)
  visible.value = false
  emit('select', cloneDeep(pendingValue.value))
}

function handleConfirm() {
  visible.value = false
  emit('select', cloneDeep(pendingValue.value))
}
</script>

<template>
  <el-popover v-model:visible="visible" placement="bottom-start" trigger="click" :width="width" @before-enter="handleOpen">
    <template #reference><slot /></template>
    <el-scrollbar max-height="280px">
      <div class="p-3 pb-0">
        <slot name="content" :value="pendingValue" />
      </div>
    </el-scrollbar>

    <div class="p-3 text-right">
      <!-- 清除多选筛选 -->
      <el-button class="min-w-12! w-12!" size="small" @click="handleReset">重置</el-button>
      <!-- 确认多选筛选 -->
      <el-button class="min-w-12! w-12!" size="small" type="primary" @click="handleConfirm">确定</el-button>
    </div>
  </el-popover>
</template>
