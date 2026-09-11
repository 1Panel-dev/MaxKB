<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted } from 'vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import { copyText } from '@/utils/clipboard'
import type { ToolInputField } from '../tool-base-node/types'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'

defineOptions({ name: 'WorkflowToolStartNode' })

const getModel = inject<() => WorkflowNodeModel>('getModel')!
const model = getModel()
const nodeConfig = model.properties.config ?? (model.properties.config = {})

const globalFields = computed(() => nodeConfig.globalFields ?? [])

function copyField(fieldValue: string) {
  copyText(`{{global.${fieldValue}}}`)
}

function formatFieldReference(fieldValue: string) {
  return `{${fieldValue}}`
}

// 基本信息的输入参数是全局变量来源，保留旧字段的 name 回退。
function refreshFieldList() {
  const toolBaseNode = model.graphModel.getNodeModelById(WorkflowNodeType.ToolBaseNode)
  const inputFields = (toolBaseNode?.properties.user_input_field_list ?? []) as ToolInputField[]
  nodeConfig.globalFields = inputFields.map((field) => ({
    label: field.label || field.name || field.field,
    value: field.field,
  }))
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
          <!-- 复制全局变量引用 -->
          <el-button class="group-hover-visible" link @click="copyField(field.value)">
            <MkIcon name="icon_copy_outlined" />
          </el-button>
        </div>
      </template>
    </div>
  </NodeContainer>
</template>
