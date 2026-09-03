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

function refreshFields() {
  const baseNode = model.graphModel.getNodeModelById(WorkflowNodeType.Base)
  const userFields = (cloneDeep(baseNode?.properties.user_input_field_list ?? []) as SourceField[]).map((field: SourceField) => ({
    label: typeof field.label === 'object' ? field.label.label : (field.label ?? field.name),
    value: field.field ?? field.variable,
  }))
  const apiFields = (cloneDeep(baseNode?.properties.api_input_field_list ?? []) as SourceField[]).map((field: SourceField) => ({
    label: field.name ?? field.variable,
    value: field.variable,
  }))
  const chatInputFields = (cloneDeep(baseNode?.properties.chat_input_field_list ?? []) as SourceField[]).map((field: SourceField) => ({
    label: field.label,
    value: field.field,
  }))

  nodeConfig.fields = [{ label: '用户问题', value: 'question' }]
  nodeConfig.globalFields = [
    { label: '当前时间', value: 'time' },
    { label: '历史聊天记录', value: 'history_context' },
    { label: '对话 ID', value: 'chat_id' },
    { label: '对话用户 ID', value: 'chat_user_id' },
    { label: '对话用户类型', value: 'chat_user_type' },
    { label: '对话用户组', value: 'chat_user_group' },
    { label: '对话用户', value: 'chat_user' },
    ...userFields,
    ...apiFields,
  ]
  nodeConfig.chatFields = chatInputFields
}

onMounted(() => {
  refreshFields()
  model.graphModel.eventCenter.on('refreshFieldList', refreshFields)
  model.graphModel.eventCenter.on('chatFieldList', refreshFields)
})

onBeforeUnmount(() => {
  model.graphModel.eventCenter.off('refreshFieldList', refreshFields)
  model.graphModel.eventCenter.off('chatFieldList', refreshFields)
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
