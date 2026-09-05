<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, ref } from 'vue'

import { createAnchorGuard, handleNodeWheel } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { WorkflowNodeField } from '@/workflow-canvas/types'
import { WorkflowMode } from '@/workflow-canvas/types'
import { iconComponent } from '../icons/utils'
import type { BaseNodeModel } from '@logicflow/core'

defineOptions({ name: 'WorkflowNodeCascader', inheritAttrs: false })

type WorkflowGraphModel = WorkflowNodeModel['graphModel'] & { getUpNodeFieldList?: (containSelf: boolean, useCache: boolean) => WorkflowNodeField[] }

const props = withDefaults(defineProps<{ global?: boolean; modelValue: string[]; nodeModel: BaseNodeModel }>(), { global: false })

const emit = defineEmits<{ 'update:modelValue': [value: string[]] }>()

const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const options = ref<WorkflowNodeField[]>([])
const nodeModel = computed(() => props.nodeModel as WorkflowNodeModel)

const selectedValue = computed({ get: () => props.modelValue, set: (value) => emit('update:modelValue', value) })
const selectedNodeField = computed(() => {
  const [nodeValue, fieldValue] = selectedValue.value ?? []
  if (!nodeValue || !fieldValue) return undefined

  const fieldGroup = options.value.find((field) => field.value === nodeValue)
  return fieldGroup?.children?.some((field) => field.value === fieldValue) ? fieldGroup : undefined
})

const getOptionsValue = () => {
  if ([WorkflowMode.ApplicationLoop, WorkflowMode.KnowledgeLoop, WorkflowMode.ToolLoop].includes(workflowMode)) {
    return props.global
      ? getUpNodeFieldList(false, true).filter(
          (field) => ['global', 'chat', 'output', 'loop'].includes(field.value) && Boolean(field.children?.length),
        )
      : getUpNodeFieldList(false, true).filter((field) => Boolean(field.children?.length))
  } else {
    return props.global
      ? nodeModel.value
          .getUpNodeFieldList(false, true)
          .filter((field) => ['global', 'chat', 'output'].includes(field.value) && Boolean(field.children?.length))
      : nodeModel.value.getUpNodeFieldList(false, true).filter((field) => Boolean(field.children?.length))
  }
}

function getUpNodeFieldList(containSelf: boolean, useCache: boolean) {
  const result = [...nodeModel.value.getUpNodeFieldList(containSelf, useCache)]
  const graphModel = props.nodeModel.graphModel as WorkflowGraphModel
  result.push(...(graphModel.getUpNodeFieldList?.(containSelf, useCache) ?? []))
  return result.filter((field) => Boolean(field.children?.length))
}
function refreshOptions(visible = true) {
  if (visible) options.value = getOptionsValue()
}

// 下拉展开期间隐藏 SVG 锚点，关闭或卸载时恢复。
const anchorGuard = createAnchorGuard(props.nodeModel)
function handleVisibleChange(visible: boolean) {
  anchorGuard.setOverlayVisible('cascader', visible)
  refreshOptions(visible)
}

function validate() {
  if (selectedValue.value.length === 0) return Promise.reject('请输入引用变量')
  if (selectedValue.value.length < 2) return Promise.reject('引用变量错误')

  const [nodeId, fieldValue] = selectedValue.value
  const fieldGroup = getOptionsValue().find(({ value }) => value === nodeId)
  if (!fieldGroup?.children?.some(({ value }) => value === fieldValue)) {
    selectedValue.value = []
    return Promise.reject('不存在的引用变量')
  }
  return Promise.resolve()
}

onMounted(() => {
  refreshOptions()
})
onBeforeUnmount(anchorGuard.reset)
defineExpose({ validate })
</script>

<template>
  <el-cascader
    v-model="selectedValue"
    v-bind="$attrs"
    :options="options"
    :teleported="false"
    clearable
    separator="/"
    @visible-change="handleVisibleChange"
    @wheel.stop
    fit-input-width
  >
    <template v-if="selectedNodeField" #prefix>
      <component :is="iconComponent(`${selectedNodeField.type}-icon`)" :size="20" :item="selectedNodeField" class="small" />
    </template>
    <template #default="{ data }">
      <span class="flex items-center gap-1" @wheel="handleNodeWheel">
        <component :is="iconComponent(`${data.type}-icon`)" :size="16" :item="data" class="small" />
        <span>{{ data.label }}</span>
      </span>
    </template>
  </el-cascader>
</template>
