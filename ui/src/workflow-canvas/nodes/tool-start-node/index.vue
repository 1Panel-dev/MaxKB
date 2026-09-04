<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted } from 'vue'
import { cloneDeep } from 'lodash'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { WorkflowNodeType, type WorkflowNodeField } from '@/workflow-canvas/types'
import { copyText } from '@/utils/clipboard'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'

defineOptions({ name: 'WorkflowToolStartNode' })

const getModel = inject('getModel') as () => WorkflowNodeModel
const model = getModel()
const nodeConfig = model.properties.config ?? (model.properties.config = {})

const globalFields = computed(() => (nodeConfig.globalFields ?? []) as WorkflowNodeField[])

function copyField(scope: 'global', fieldValue: string) {
  copyText(`{{${scope}.${fieldValue}}}`)
}

function formatFieldReference(fieldValue: string) {
  return `{${fieldValue}}`
}

function getRefreshFieldList() {
  const toolBaseNode = model.graphModel.getNodeModelById(WorkflowNodeType.ToolBaseNode)
  const userFields = (cloneDeep(toolBaseNode?.properties.user_input_field_list ?? []) as any[]).map((field: any) => ({
    label: field.label || field.name,
    value: field.field,
  }))
  return [...userFields]
}

function refreshFieldList() {
  nodeConfig.globalFields = [...getRefreshFieldList()]
}

onMounted(() => {
  refreshFieldList()
  model.graphModel.eventCenter.on('refreshFieldList', refreshFieldList)
})

onBeforeUnmount(() => {
  model.graphModel.eventCenter.off('refreshFieldList', refreshFieldList)
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">全局变量</h6>
    <div class="mk-gray-card space-y-4">
      <template v-for="field in globalFields" :key="field.value">
        <div class="group flex-between">
          <span class="break-all">{{ field.label }} {{ formatFieldReference(field.value) }}</span>
          <el-button class="group-hover-visible" link @click="copyField('global', field.value)">
            <MkIcon name="icon_copy_outlined" />
          </el-button>
        </div>
      </template>
    </div>
  </NodeContainer>
</template>