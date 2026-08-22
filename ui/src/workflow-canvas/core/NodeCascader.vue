<script setup lang="ts">
import { computed, inject, onMounted, ref } from 'vue'

import { handleNodeWheel } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { WorkflowNodeField } from '@/workflow-canvas/types'
import { WorkflowMode } from '@/workflow-canvas/types'
import { iconComponent } from '../icons/utils'
import type { BaseNodeModel } from '@logicflow/core'

defineOptions({ name: 'WorkflowNodeCascader', inheritAttrs: false })

type WorkflowGraphModel = WorkflowNodeModel['graphModel'] & {
  getUpNodeFieldList?: (containSelf: boolean, useCache: boolean) => WorkflowNodeField[]
}

const props = withDefaults(
  defineProps<{
    global?: boolean
    modelValue: string[]
    nodeModel: BaseNodeModel
  }>(),
  { global: false },
)

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const options = ref<WorkflowNodeField[]>([])

const selectedValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const getOptionsValue = () => {
  if (
    [WorkflowMode.ApplicationLoop, WorkflowMode.KnowledgeLoop, WorkflowMode.ToolLoop].includes(
      workflowMode,
    )
  ) {
    return props.global
      ? getUpNodeFieldList(false, true).filter(
          (field) =>
            ['global', 'chat', 'output', 'loop'].includes(field.value) &&
            Boolean(field.children?.length),
        )
      : getUpNodeFieldList(false, true).filter((field) => Boolean(field.children?.length))
  } else {
    return props.global
      ? props.nodeModel
          .getUpNodeFieldList(false, true)
          .filter(
            (field) =>
              ['global', 'chat', 'output'].includes(field.value) && Boolean(field.children?.length),
          )
      : props.nodeModel
          .getUpNodeFieldList(false, true)
          .filter((field) => Boolean(field.children?.length))
  }
}

function getUpNodeFieldList(containSelf: boolean, useCache: boolean) {
  const result = [...props.nodeModel.getUpNodeFieldList(containSelf, useCache)]
  const graphModel = props.nodeModel.graphModel as WorkflowGraphModel
  result.push(...(graphModel.getUpNodeFieldList?.(containSelf, useCache) ?? []))
  return result.filter((field) => Boolean(field.children?.length))
}
function refreshOptions(visible = true) {
  if (visible) options.value = getOptionsValue()
}

function validate() {
  if (selectedValue.value.length === 0) return Promise.reject('引用变量必填')
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
defineExpose({ validate })
</script>

<template>
  <el-cascader
    v-model="selectedValue"
    v-bind="$attrs"
    :options="options"
    :teleported="false"
    clearable
    separator=" > "
    @visible-change="refreshOptions"
    @wheel.stop
  >
    <template #default="{ data }">
      <span class="flex align-center" @wheel="handleNodeWheel">
        <component
          :is="iconComponent(`${data.type}-icon`)"
          class="mr-8"
          :size="18"
          :item="data"
          style="--el-avatar-border-radius: 6px"
        />{{ data.label }}</span
      >
    </template>
  </el-cascader>
</template>
