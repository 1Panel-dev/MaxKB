<script setup lang="ts">
import { computed, ref } from 'vue'
import type { CheckboxValueType } from 'element-plus'
import type { TableFilterOption } from './types'

defineOptions({ name: 'TableFilterMultiple' })
const props = withDefaults(
  defineProps<{
    modelValue: CheckboxValueType[]
    options: TableFilterOption[]
    width?: string | number
  }>(),
  { width: 192 },
)
const emit = defineEmits<{ select: [value: CheckboxValueType[]]; open: [] }>()
defineSlots<{ default(): unknown }>()

// 打开时回填草稿，确认或重置后提交。
const visible = ref(false)
const pendingValues = ref<CheckboxValueType[]>([])
const allOptionValues = computed(() => props.options.filter((option) => !option.disabled).map(({ value }) => value))
const allSelected = computed(() => allOptionValues.value.length > 0 && allOptionValues.value.every((value) => pendingValues.value.includes(value)))
const selectionIndeterminate = computed(() => allOptionValues.value.some((value) => pendingValues.value.includes(value)) && !allSelected.value)

function handleOpen() {
  pendingValues.value = [...props.modelValue]
  emit('open')
}

function handleSelectAllChange(checked: CheckboxValueType) {
  const disabledValues = pendingValues.value.filter((value) => props.options.some((option) => option.value === value && option.disabled))
  pendingValues.value = checked ? [...disabledValues, ...allOptionValues.value] : disabledValues
}

function handleReset() {
  pendingValues.value = []
  visible.value = false
  emit('select', [])
}

function handleConfirm() {
  visible.value = false
  emit('select', [...pendingValues.value])
}
</script>

<template>
  <el-popover v-model:visible="visible" placement="bottom-start" trigger="click" :width="width" @before-enter="handleOpen">
    <template #reference><slot /></template>
    <el-scrollbar max-height="280px">
      <div class="flex-column gap-2 p-3 pb-0">
        <el-checkbox :indeterminate="selectionIndeterminate" :model-value="allSelected" class="mr-0!" @change="handleSelectAllChange">
          全部
        </el-checkbox>
        <el-checkbox-group v-model="pendingValues" class="flex-column gap-2">
          <el-checkbox
            v-for="option in options"
            :key="`${typeof option.value}:${option.value}`"
            :value="option.value"
            :disabled="option.disabled"
            class="mk-table-filter__option mr-0! w-full min-w-0"
          >
            <span class="block min-w-0 truncate" :title="option.label">{{ option.label }}</span>
          </el-checkbox>
        </el-checkbox-group>
      </div>
    </el-scrollbar>

    <div class="p-3 text-right">
      <!-- 清除多选筛选 -->
      <el-button class="min-w-12! w-12!" size="small" @click="handleReset">重置</el-button>
      <!-- 确认多选筛选 -->
      <el-button class="min-w-12! w-12!" :disabled="pendingValues.length === 0" size="small" type="primary" @click="handleConfirm">确定</el-button>
    </div>
  </el-popover>
</template>

<style scoped lang="scss">
/* 多选选项 */
.mk-table-filter__option {
  :deep(.el-checkbox__label) {
    min-width: 0;
    overflow: hidden;
  }
}
</style>
