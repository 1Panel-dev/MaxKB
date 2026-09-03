<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted } from 'vue'
import { cloneDeep } from 'lodash'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { WorkflowNodeType, type WorkflowNodeField } from '@/workflow-canvas/types'
import { copyText } from '@/utils/clipboard'
import type { BaseNodeModel } from '@logicflow/core'

defineOptions({ name: 'WorkflowStartNode' })

interface SourceField {
  field?: string
  label?: string | { label?: string }
  name?: string
  variable?: string
}

type FileUploadField = 'audio' | 'document' | 'image' | 'other' | 'video'

interface BaseNodeData {
  file_upload_enable?: boolean
  file_upload_setting?: Partial<Record<FileUploadField, boolean>>
  long_term_enable?: boolean
}

const fileUploadFields: Array<{ label: string; value: FileUploadField }> = [
  { label: '文档', value: 'document' },
  { label: '图片', value: 'image' },
  { label: '音频', value: 'audio' },
  { label: '视频', value: 'video' },
  { label: '其他', value: 'other' },
]
const fileUploadFieldValues = new Set<FileUploadField>(fileUploadFields.map(({ value }) => value))

const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel()
const nodeConfig = model.properties.config ?? (model.properties.config = {})

const globalFields = computed(() => (nodeConfig.globalFields ?? []) as WorkflowNodeField[])
const chatFields = computed(() => (nodeConfig.chatFields ?? []) as WorkflowNodeField[])

function copyField(scope: 'chat' | 'global', fieldValue: string) {
  copyText(`{{${scope}.${fieldValue}}}`)
}

function formatFieldReference(fieldValue: string) {
  return `{${fieldValue}}`
}

// 同步基本信息节点配置到开始节点的可用输出字段。
function getBaseNode() {
  return model.graphModel.getNodeModelById(WorkflowNodeType.Base)
}

function refreshStartQuestionField() {
  const questionFields = [{ label: '用户问题', value: 'question' }]
  nodeConfig.fields = questionFields
  model.properties.fields = questionFields
}

function getRefreshFieldList() {
  const baseNode = getBaseNode()
  const userFields = (cloneDeep(baseNode?.properties.user_input_field_list ?? []) as SourceField[]).map((field: SourceField) => ({
    label: typeof field.label === 'object' ? field.label.label : (field.label ?? field.name),
    value: field.field ?? field.variable,
  }))
  const apiFields = (cloneDeep(baseNode?.properties.api_input_field_list ?? []) as SourceField[]).map((field: SourceField) => ({
    label: field.name ?? field.variable,
    value: field.variable,
  }))
  return [...userFields, ...apiFields]
}

function refreshFieldList() {
  nodeConfig.globalFields = [
    { label: '当前时间', value: 'time' },
    { label: '历史聊天记录', value: 'history_context' },
    { label: '对话 ID', value: 'chat_id' },
    { label: '对话用户 ID', value: 'chat_user_id' },
    { label: '对话用户类型', value: 'chat_user_type' },
    { label: '对话用户组', value: 'chat_user_group' },
    { label: '对话用户', value: 'chat_user' },
    ...getRefreshFieldList(),
  ]
}

function refreshChatFieldList() {
  const baseNode = getBaseNode()
  nodeConfig.chatFields = (cloneDeep(baseNode?.properties.chat_input_field_list ?? []) as SourceField[]).map((field) => ({
    label: field.label,
    value: field.field,
  }))
}

function refreshFileUploadConfig() {
  const fields = (cloneDeep(nodeConfig.fields ?? []) as WorkflowNodeField[]).filter(
    ({ value }) => !fileUploadFieldValues.has(value as FileUploadField),
  )
  const baseNodeData = getBaseNode()?.properties.node_data as BaseNodeData | undefined
  if (!baseNodeData?.file_upload_enable) {
    nodeConfig.fields = fields
    return
  }

  const enabledFileFields = fileUploadFields.filter(({ value }) => baseNodeData.file_upload_setting?.[value])
  nodeConfig.fields = [...fields, ...enabledFileFields]
}

function refreshLongTermConfig() {
  const fields = (cloneDeep(nodeConfig.fields ?? []) as WorkflowNodeField[]).filter(({ value }) => value !== 'memory')
  const baseNodeData = getBaseNode()?.properties.node_data as BaseNodeData | undefined
  nodeConfig.fields = baseNodeData?.long_term_enable ? [...fields, { label: '长期记忆', value: 'memory' }] : fields
}

onMounted(() => {
  refreshStartQuestionField()
  refreshChatFieldList()
  refreshFieldList()
  refreshFileUploadConfig()
  refreshLongTermConfig()
  model.graphModel.eventCenter.on('refreshFieldList', refreshFieldList)
  model.graphModel.eventCenter.on('chatFieldList', refreshChatFieldList)
  model.graphModel.eventCenter.on('refreshFileUploadConfig', refreshFileUploadConfig)
  model.graphModel.eventCenter.on('refreshLongTermConfig', refreshLongTermConfig)
})

onBeforeUnmount(() => {
  model.graphModel.eventCenter.off('refreshFieldList', refreshFieldList)
  model.graphModel.eventCenter.off('chatFieldList', refreshChatFieldList)
  model.graphModel.eventCenter.off('refreshFileUploadConfig', refreshFileUploadConfig)
  model.graphModel.eventCenter.off('refreshLongTermConfig', refreshLongTermConfig)
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

    <template v-if="chatFields.length">
      <h6 class="mk-title-decoration my-2">会话变量</h6>
      <div class="mk-gray-card space-y-4">
        <template v-for="field in chatFields" :key="field.value">
          <div class="group flex-between">
            <span class="break-all">{{ field.label }} {{ formatFieldReference(field.value) }}</span>
            <el-button class="group-hover-visible" link @click="copyField('chat', field.value)">
              <MkIcon name="icon_copy_outlined" />
            </el-button>
          </div>
        </template>
      </div>
    </template>
  </NodeContainer>
</template>
