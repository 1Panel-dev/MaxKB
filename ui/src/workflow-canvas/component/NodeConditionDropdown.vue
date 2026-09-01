<script setup lang="ts">
import type { BaseNodeModel } from '@logicflow/core'
import { computed } from 'vue'
import { set } from 'lodash'

import { WorkflowKind, WorkflowNodeType } from '@/workflow-canvas/types'

defineOptions({ name: 'NodeConditionDropdown' })

const props = defineProps<{ model: BaseNodeModel }>()
const emit = defineEmits<{
  'visible-change': [visible: boolean]
}>()

type NodeConditionProperties = {
  condition?: boolean | 'AND' | 'OR'
  kind?: WorkflowKind
}

const nodeProperties = computed(() => props.model.properties as unknown as NodeConditionProperties)
const visible = computed(() => {
  return (
    ![
      WorkflowNodeType.Start,
      WorkflowNodeType.Base,
      WorkflowNodeType.ToolBaseNode,
      WorkflowNodeType.ToolStartNode,
      WorkflowNodeType.KnowledgeBase,
      WorkflowNodeType.LoopStartNode.toString(),
      WorkflowNodeType.DataSourceLocalNode,
      WorkflowNodeType.DataSourceWebNode,
    ].includes(String(props.model.type)) && nodeProperties.value.kind !== WorkflowKind.DataSource
  )
})
const condition = computed({
  get: () => {
    if (nodeProperties.value.condition) return nodeProperties.value.condition

    set(props.model.properties, 'condition', 'AND')
    return true
  },
  set: (value: boolean | 'AND' | 'OR') => {
    set(props.model.properties, 'condition', value)
  },
})
</script>

<template>
  <MkDropdown v-if="visible" :teleported="false" trigger="click" placement="bottom-start" @visible-change="emit('visible-change', $event)">
    <el-button text>条件</el-button>
    <template #dropdown>
      <div class="w-[280px] px-4 py-3">
        <h5>执行条件</h5>
        <p class="mt-2 text-N600">
          <span>前置</span>
          <el-select v-model="condition" class="mx-2 w-[60px]" size="small">
            <el-option label="所有" value="AND" />
            <el-option label="任一" value="OR" />
          </el-select>
          <span>连线节点执行完，执行当前节点</span>
        </p>
      </div>
    </template>
  </MkDropdown>
</template>
