<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { BaseNodeModel } from '@logicflow/core'
import type { FormInstance } from 'element-plus'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import { START_NODE_REFERENCES } from '@/workflow-canvas/config/constants'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { createAnchorGuard, handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import { REPLY_CONTENT_TYPE_LABELS } from './constant'

defineOptions({ name: 'WorkflowReplyNode' })
const { t } = useI18n({ useScope: 'global' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel()
const anchorGuard = createAnchorGuard(model)
onBeforeUnmount(() => anchorGuard.reset())
interface ReplyNodeForm {
  content: string
  content_type: 'TEXT' | 'HTML' | 'TOOL'
  fields: string[]
  is_result: boolean
  reply_type: 'content' | 'referencing'
}

const formRef = useTemplateRef<FormInstance>('formRef')

const defaultForm: ReplyNodeForm = {
  content: '',
  content_type: 'TEXT',
  fields: [],
  is_result: true,
  reply_type: 'content',
}
const savedForm = model.properties.node_data as Partial<ReplyNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  content: savedForm?.content ?? defaultForm.content,
  content_type: savedForm?.content_type ?? defaultForm.content_type,
  fields: Array.isArray(savedForm?.fields) ? savedForm.fields : [],
  is_result: savedForm ? savedForm.is_result : defaultForm.is_result,
  reply_type: savedForm?.reply_type ?? defaultForm.reply_type,
}

const formData = computed<ReplyNodeForm>({
  get: () => model.properties.node_data as ReplyNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const contentPlaceholder = computed(() => {
  if (formData.value.content_type === 'TOOL') {
    return JSON.stringify([{ id: 'call_1', name: 'get_weather', arguments: '{}', content: t('workflow.reply.format.toolExampleContent') }])
  }
  if (formData.value.content_type === 'HTML') {
    return `<p>${t('workflow.reply.content.htmlPlaceholder', { reference: START_NODE_REFERENCES.question })}</p>`
  }
  return t('workflow.reply.content.placeholder', { reference: START_NODE_REFERENCES.question })
})

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  if (formData.value.is_result === undefined && isLastNode(model)) {
    formData.value.is_result = true
  }
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <div class="mk-gray-card">
      <el-form
        ref="formRef"
        :model="formData"
        :validate-on-rule-change="false"
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent
      >
        <!-- 回复类型 -->
        <el-form-item :label="t('workflow.reply.format.typeLabel')">
          <el-select
            v-model="formData.content_type"
            :teleported="false"
            @visible-change="anchorGuard.setOverlayVisible('content-type', $event)"
            @wheel="handleNodeWheel"
          >
            <el-option :label="REPLY_CONTENT_TYPE_LABELS.TEXT" value="TEXT" />
            <el-option :label="REPLY_CONTENT_TYPE_LABELS.HTML" value="HTML" />
            <el-option :label="REPLY_CONTENT_TYPE_LABELS.TOOL" value="TOOL">
              <div class="flex-align-center gap-1">
                <span>{{ REPLY_CONTENT_TYPE_LABELS.TOOL }}</span>
                <MkTooltip :content="t('workflow.reply.format.toolDescription')" placement="right">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </MkTooltip>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item
          :label="t('workflow.reply.content.label')"
          class="mk-hide-asterisk"
          :prop="formData.reply_type === 'referencing' ? 'fields' : 'content'"
          :rules="{
            type: formData.reply_type === 'referencing' ? 'array' : 'string',
            required: true,
            whitespace: formData.reply_type !== 'referencing',
            message:
              formData.reply_type === 'referencing' ? t('workflow.variable.selectRequiredMessage') : t('workflow.reply.content.requiredMessage'),
            trigger: 'change',
          }"
        >
          <template #label>
            <div class="flex-between">
              <span class="mk-required">{{ t('workflow.reply.content.label') }}</span>
              <!-- 选择回复内容来源 -->
              <el-select v-model="formData.reply_type" :teleported="false" class="w-21!" size="small">
                <el-option :label="t('workflow.referenceVariable.label')" value="referencing" />
                <el-option :label="t('workflow.reply.content.custom')" value="content" />
              </el-select>
            </div>
          </template>

          <NodeCascader
            v-if="formData.reply_type === 'referencing'"
            ref="nodeCascaderRef"
            v-model="formData.fields"
            :node-model="model"
            :placeholder="t('workflow.variable.selectPlaceholder')"
          />

          <MdEditorMagnify
            v-else
            @wheel="handleNodeWheel"
            :title="t('workflow.reply.content.label')"
            v-model="formData.content"
            :placeholder="contentPlaceholder"
          />
        </el-form-item>

        <!-- 返回内容 -->
        <div class="flex-between w-full">
          <span class="flex-align-center gap-1">
            {{ t('workflow.returnContent.label') }}
            <MkTooltip :content="t('workflow.returnContent.description')" placement="right">
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </MkTooltip>
          </span>
          <span>
            <el-switch v-model="formData.is_result" size="small" />
          </span>
        </div>
      </el-form>
    </div>
  </NodeContainer>
</template>
