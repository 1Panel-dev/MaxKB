<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { cloneDeep, isEqual } from 'lodash'
import type { CascaderNode, CascaderOption, CascaderPanelInstance, CascaderProps, CascaderValue } from 'element-plus'

defineOptions({ name: 'TableFilterCascader' })
const props = withDefaults(
  defineProps<{
    modelValue: CascaderValue | null | undefined
    options: CascaderOption[]
    cascaderProps?: CascaderProps
    width?: string | number
  }>(),
  { width: 'auto' },
)
const emit = defineEmits<{ select: [value: CascaderValue | null]; open: [] }>()
defineSlots<{ default(): unknown }>()

// 级联即时提交；多选保持面板打开。
const visible = ref(false)
const cascaderConfig = computed<CascaderProps>(() => ({
  multiple: true,
  checkStrictly: true,
  emitPath: false,
  showPrefix: false,
  ...props.cascaderProps,
}))

// 面板保留父子独立选择；对外返回叶子值，模型回写不覆盖原始勾选。
const panelRef = ref<CascaderPanelInstance>()
const panelValue = ref<CascaderValue | null | undefined>(cloneDeep(props.modelValue))
let submittedValue = cloneDeep(props.modelValue)

watch(
  () => props.modelValue,
  (value) => {
    if (isEqual(value, submittedValue)) return
    panelValue.value = cloneDeep(value)
    submittedValue = cloneDeep(value)
  },
  { deep: true },
)

function getSelectedLeafValues() {
  const selectedLeaves = new Map<number, CascaderNode>()
  function collectLeaves(node: CascaderNode) {
    if (node.isDisabled) return
    if (node.isLeaf) selectedLeaves.set(node.uid, node)
    else node.children.forEach(collectLeaves)
  }
  panelRef.value?.getCheckedNodes(false).forEach(collectLeaves)
  return [...selectedLeaves.values()].map((node) => node.valueByOption)
}

function handleChange(value: CascaderValue | null | undefined) {
  panelValue.value = cloneDeep(value)
  const { multiple, checkStrictly, lazy } = cascaderConfig.value
  // 静态独立多选将父组展开为叶子；联动选择本身已返回叶子，懒加载沿用原始协议。
  const nextValue = multiple && checkStrictly && !lazy && panelRef.value ? getSelectedLeafValues() : (value ?? (multiple ? [] : null))
  submittedValue = cloneDeep(nextValue)
  if (!multiple) visible.value = false
  emit('select', nextValue)
}
</script>

<template>
  <el-popover v-model:visible="visible" placement="bottom-start" trigger="click" :width="width" @before-enter="emit('open')">
    <template #reference><slot /></template>
    <el-cascader-panel
      v-if="visible"
      ref="panelRef"
      :model-value="panelValue"
      :options="options"
      :props="cascaderConfig"
      @change="handleChange"
      class="border-none!"
    />
  </el-popover>
</template>
