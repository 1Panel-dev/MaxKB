<script setup lang="ts">
import { CopyDocument } from '@element-plus/icons-vue'
import { cloneDeep, set } from 'lodash'
import type { WorkflowNodeField, WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import NodeContainer from '@/workflow-canvas/core/NodeContainer.vue'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'WorkflowStartNode' })

interface SourceField {
  field?: string
  label?: string | { label?: string }
  name?: string
  variable?: string
}

const props = defineProps<{ nodeModel: WorkflowNodeModel }>()
const nodeModel = props.nodeModel
const nodeConfig = nodeModel.properties.config ?? (nodeModel.properties.config = {})

const globalFields = computed(() => (nodeConfig.globalFields ?? []) as WorkflowNodeField[])
const chatFields = computed(() => (nodeConfig.chatFields ?? []) as WorkflowNodeField[])

function copyField(scope: 'chat' | 'global', fieldValue: string) {
  copyText(`{{${scope}.${fieldValue}}}`)
}

function formatFieldReference(fieldValue: string) {
  return `{${fieldValue}}`
}

function refreshFields() {
  const baseNode = props.nodeModel.graphModel.getNodeModelById(WorkflowNodeType.Base)
  const userFields = (
    cloneDeep(baseNode?.properties.user_input_field_list ?? []) as SourceField[]
  ).map((field: SourceField) => ({
    label: typeof field.label === 'object' ? field.label.label : (field.label ?? field.name),
    value: field.field ?? field.variable,
  }))
  const apiFields = (
    cloneDeep(baseNode?.properties.api_input_field_list ?? []) as SourceField[]
  ).map((field: SourceField) => ({
    label: field.name ?? field.variable,
    value: field.variable,
  }))
  const chatInputFields = (
    cloneDeep(baseNode?.properties.chat_input_field_list ?? []) as SourceField[]
  ).map((field: SourceField) => ({ label: field.label, value: field.field }))

  set(nodeConfig, 'fields', [{ label: '用户问题', value: 'question' }])
  set(nodeConfig, 'globalFields', [
    { label: '当前时间', value: 'time' },
    { label: '历史聊天记录', value: 'history_context' },
    { label: '对话 ID', value: 'chat_id' },
    { label: '对话用户 ID', value: 'chat_user_id' },
    { label: '对话用户类型', value: 'chat_user_type' },
    { label: '对话用户组', value: 'chat_user_group' },
    { label: '对话用户', value: 'chat_user' },
    ...userFields,
    ...apiFields,
  ])
  set(nodeConfig, 'chatFields', chatInputFields)
}

onMounted(() => {
  refreshFields()
  props.nodeModel.graphModel.eventCenter.on('refreshFieldList', refreshFields)
  props.nodeModel.graphModel.eventCenter.on('chatFieldList', refreshFields)
})

onBeforeUnmount(() => {
  props.nodeModel.graphModel.eventCenter.off('refreshFieldList', refreshFields)
  props.nodeModel.graphModel.eventCenter.off('chatFieldList', refreshFields)
})
</script>

<template>
  <NodeContainer :node-model="props.nodeModel">
    <h6 class="mb-2">全局变量</h6>
    <div class="rounded-md bg-N100 px-3 py-1 text-N600">
      <div
        v-for="field in globalFields"
        :key="field.value"
        class="flex items-center justify-between gap-2 py-2"
      >
        <span>{{ field.label }} {{ formatFieldReference(field.value) }}</span>
        <el-button link @click="copyField('global', field.value)">
          <MkIcon :icon="CopyDocument" />
        </el-button>
      </div>
    </div>

    <template v-if="chatFields.length">
      <h6 class="mb-2 mt-4">会话变量</h6>
      <div class="rounded-md bg-N100 px-3 py-1 text-N600">
        <div
          v-for="field in chatFields"
          :key="field.value"
          class="flex items-center justify-between gap-2 py-2"
        >
          <span>{{ field.label }} {{ formatFieldReference(field.value) }}</span>
          <el-button link @click="copyField('chat', field.value)">
            <MkIcon :icon="CopyDocument" />
          </el-button>
        </div>
      </div>
    </template>
  </NodeContainer>
</template>
