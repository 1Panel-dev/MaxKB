<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { WorkflowNodeField } from '@/workflow-canvas/types'
import type { BaseNodeModel } from '@logicflow/core'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'WorkflowStartNode' })

const { t } = useI18n({ useScope: 'global' })

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

const fileUploadFields: FileUploadField[] = ['document', 'image', 'audio', 'video', 'other']
const fileUploadFieldValues = new Set<FileUploadField>(fileUploadFields)

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
  const questionFields = [{ label: t('workflow.start.question'), value: 'question' }]
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
    { label: t('workflow.start.currentTime'), value: 'time' },
    { label: t('workflow.history.label'), value: 'history_context' },
    { label: t('workflow.start.chatId'), value: 'chat_id' },
    { label: t('workflow.start.chatUserId'), value: 'chat_user_id' },
    { label: t('workflow.start.chatUserType'), value: 'chat_user_type' },
    { label: t('workflow.start.chatUserGroup'), value: 'chat_user_group' },
    { label: t('workflow.start.chatUser'), value: 'chat_user' },
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

  const enabledFileFields = fileUploadFields
    .filter((value) => baseNodeData.file_upload_setting?.[value])
    .map((value) => ({ label: t(`upload.types.${value}`), value }))
  nodeConfig.fields = [...fields, ...enabledFileFields]
}

function refreshLongTermConfig() {
  const fields = (cloneDeep(nodeConfig.fields ?? []) as WorkflowNodeField[]).filter(({ value }) => value !== 'memory')
  const baseNodeData = getBaseNode()?.properties.node_data as BaseNodeData | undefined
  nodeConfig.fields = baseNodeData?.long_term_enable ? [...fields, { label: t('application.longTermMemory.label'), value: 'memory' }] : fields
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
    <h6 class="mk-title-decoration mb-2">{{ t('workflow.globalVariables.title') }}</h6>
    <div class="mk-gray-card space-y-4">
      <template v-for="field in globalFields" :key="field.value">
        <div class="group flex-between">
          <span class="break-all">{{ field.label }} {{ formatFieldReference(field.value) }}</span>
          <!-- 复制全局变量引用 -->
          <el-button class="group-hover-visible" link @click="copyField('global', field.value)">
            <MkIcon name="icon_copy_outlined" />
          </el-button>
        </div>
      </template>
    </div>

    <template v-if="chatFields.length">
      <h6 class="mk-title-decoration my-2">{{ t('workflow.conversationVariables.title') }}</h6>
      <div class="mk-gray-card space-y-4">
        <template v-for="field in chatFields" :key="field.value">
          <div class="group flex-between">
            <span class="break-all">{{ field.label }} {{ formatFieldReference(field.value) }}</span>
            <!-- 复制会话变量引用 -->
            <el-button class="group-hover-visible" link @click="copyField('chat', field.value)">
              <MkIcon name="icon_copy_outlined" />
            </el-button>
          </div>
        </template>
      </div>
    </template>
  </NodeContainer>
</template>
