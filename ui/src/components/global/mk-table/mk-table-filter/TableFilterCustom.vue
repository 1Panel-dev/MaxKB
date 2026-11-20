<script setup lang="ts">
import { ref } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { TableFilterCustomValue } from './types'

defineOptions({ name: 'TableFilterCustom' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{
  modelValue: TableFilterCustomValue
  resetValue: TableFilterCustomValue
  width?: string | number
}>()

const emit = defineEmits<{ select: [value: TableFilterCustomValue]; open: [] }>()
defineSlots<{ default(): unknown; content(props: { value: TableFilterCustomValue }): unknown }>()

// 插槽只编辑独立草稿，确定或重置才回写已生效的筛选。
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
      <!-- 重置自定义筛选 -->
      <el-button plain class="min-w-12!" size="small" @click="handleReset">{{ t('common.actions.reset') }}</el-button>
      <!-- 确定自定义筛选 -->
      <el-button class="min-w-12!" size="small" type="primary" @click="handleConfirm">{{ t('common.actions.comfirm') }}</el-button>
    </div>
  </el-popover>
</template>
