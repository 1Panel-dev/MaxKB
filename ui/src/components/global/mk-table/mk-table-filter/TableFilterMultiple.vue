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
    filterable?: boolean
  }>(),
  { width: 192, filterable: false },
)
const emit = defineEmits<{ select: [value: CheckboxValueType[]]; open: [] }>()
defineSlots<{ default(): unknown }>()

// 打开时回填草稿，确认或重置后提交。
const visible = ref(false)
const pendingValues = ref<CheckboxValueType[]>([])
const searchKeyword = ref('')
const filteredOptions = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  return props.filterable && keyword ? props.options.filter((option) => option.label.toLowerCase().includes(keyword)) : props.options
})
const allOptionValues = computed(() => filteredOptions.value.filter((option) => !option.disabled).map(({ value }) => value))
const allSelected = computed(() => allOptionValues.value.length > 0 && allOptionValues.value.every((value) => pendingValues.value.includes(value)))
const selectionIndeterminate = computed(() => allOptionValues.value.some((value) => pendingValues.value.includes(value)) && !allSelected.value)

function handleOpen() {
  searchKeyword.value = ''
  pendingValues.value = [...props.modelValue]
  emit('open')
}

function handleSelectAllChange(checked: CheckboxValueType) {
  // 搜索时保留隐藏的勾选项；未开启搜索时沿用原有全选规则。
  const retainedValues = pendingValues.value.filter((value) =>
    props.filterable ? !allOptionValues.value.includes(value) : props.options.some((option) => option.value === value && option.disabled),
  )
  pendingValues.value = checked ? [...new Set([...retainedValues, ...allOptionValues.value])] : retainedValues
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
    <div v-if="filterable" class="px-3 pt-3">
      <MkSearchInput v-model="searchKeyword" />
    </div>
    <el-scrollbar max-height="280px">
      <div class="flex-column gap-2 p-3 pb-0">
        <el-checkbox
          :indeterminate="selectionIndeterminate"
          :model-value="allSelected"
          :disabled="filterable && !allOptionValues.length"
          class="mr-0!"
          @change="handleSelectAllChange"
        >
          全部
        </el-checkbox>
        <el-checkbox-group v-model="pendingValues" class="mk-checkbox-group-vertical gap-2">
          <el-checkbox
            v-for="option in filteredOptions"
            :key="`${typeof option.value}:${option.value}`"
            :value="option.value"
            :disabled="option.disabled"
          >
            <span class="block min-w-0 truncate" :title="option.label">{{ option.label }}</span>
          </el-checkbox>
        </el-checkbox-group>
        <MkEmpty v-if="filterable && !filteredOptions.length" type="search" description="暂无匹配结果" :image-size="64" />
      </div>
    </el-scrollbar>

    <div class="p-3 text-right">
      <!-- 清除多选筛选 -->
      <el-button plain class="min-w-12! w-12!" size="small" @click="handleReset">重置</el-button>
      <!-- 确认多选筛选 -->
      <el-button class="min-w-12! w-12!" size="small" type="primary" @click="handleConfirm">确定</el-button>
    </div>
  </el-popover>
</template>

<style scoped lang="scss"></style>
