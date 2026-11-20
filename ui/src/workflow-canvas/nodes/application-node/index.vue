<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { FormInstance } from 'element-plus'
import { APPLICATION_TYPE } from '@/api/enums'
import ApplicationApi from '@/api/admin/workspace/application/application'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { WorkflowMode, WorkflowNodeType } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowApplicationNode' })

const { t } = useI18n({ useScope: 'global' })

type FieldLabel = string | { label?: string }
type UploadField = 'audio' | 'document' | 'image' | 'video'
type UploadListKey = `${UploadField}_list`

interface ApplicationApiInputField {
  is_required: boolean
  label?: FieldLabel
  value: string[]
  variable: FieldLabel
}

interface ApplicationUserInputField {
  field: string
  label: FieldLabel
  required: boolean
  value: string[]
}

interface ApplicationNodeForm {
  api_input_field_list: ApplicationApiInputField[]
  application_id?: string
  audio_list?: string[]
  document_list?: string[]
  icon?: string
  image_list?: string[]
  is_result: boolean
  name?: string
  question_reference_address: string[]
  user_input_field_list: ApplicationUserInputField[]
  video_list?: string[]
}

interface ReferencedApplicationProperties {
  api_input_field_list?: ApplicationApiInputField[]
  node_data?: {
    file_upload_enable?: boolean
    file_upload_setting?: Partial<Record<UploadField, boolean>>
  }
  user_input_field_list?: ApplicationUserInputField[]
}

const uploadFields: UploadField[] = ['document', 'image', 'audio', 'video']
const getModel = inject('getModel') as () => WorkflowNodeModel
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

const formRef = useTemplateRef<FormInstance>('formRef')

// 一次性补齐旧节点表单，保留已保存的参数和文件引用。
const defaultForm: ApplicationNodeForm = {
  api_input_field_list: [],
  user_input_field_list: [],
  question_reference_address: [WorkflowNodeType.Start, 'question'],
  is_result: false,
}
const savedForm = model.properties.node_data as Partial<ApplicationNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  api_input_field_list: Array.isArray(savedForm?.api_input_field_list) ? savedForm.api_input_field_list : defaultForm.api_input_field_list,
  user_input_field_list: Array.isArray(savedForm?.user_input_field_list) ? savedForm.user_input_field_list : defaultForm.user_input_field_list,
  question_reference_address: Array.isArray(savedForm?.question_reference_address)
    ? savedForm.question_reference_address
    : defaultForm.question_reference_address,
  is_result: savedForm?.is_result ?? defaultForm.is_result,
}

const formData = computed<ApplicationNodeForm>({
  get: () => model.properties.node_data as ApplicationNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const showReturnContent = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function formatFieldLabel(label: FieldLabel) {
  return typeof label === 'object' && label !== null ? (label.label ?? '') : label
}

// 根据关联智能体配置同步输入字段，按字段标识保留已选变量。
function syncUploadField(field: UploadField, enabled: boolean) {
  const listKey: UploadListKey = `${field}_list`
  if (enabled) {
    if (!Array.isArray(formData.value[listKey])) formData.value[listKey] = []
    return
  }
  delete formData.value[listKey]
}

function mergeApiInputFields(fields: ApplicationApiInputField[] = []) {
  const previousFields = cloneDeep(formData.value.api_input_field_list)
  formData.value.api_input_field_list = fields.map((field) => {
    const previousField = previousFields.find((item) => JSON.stringify(item.variable) === JSON.stringify(field.variable))
    return {
      ...field,
      label: formatFieldLabel(field.label ?? field.variable),
      value: previousField?.value ?? field.value ?? [],
    }
  })
}

function mergeUserInputFields(fields: ApplicationUserInputField[] = []) {
  const previousFields = cloneDeep(formData.value.user_input_field_list)
  formData.value.user_input_field_list = fields.map((field) => {
    const previousField = previousFields.find((item) => item.field === field.field)
    return {
      ...field,
      label: formatFieldLabel(field.label),
      value: previousField?.value ?? field.value ?? [],
    }
  })
}

function refreshApplicationFields() {
  const applicationId = formData.value.application_id
  if (!applicationId) {
    model.properties.status = 500
    return
  }

  ApplicationApi.getApplicationDetail(applicationId)
    .then((application) => {
      formData.value.name = application.name

      if (application.type === APPLICATION_TYPE.WORK_FLOW) {
        const startNode = application.work_flow?.nodes?.[0]
        if (!startNode) {
          model.properties.status = 500
          return
        }

        const startProperties = (startNode.properties ?? {}) as ReferencedApplicationProperties
        mergeApiInputFields(cloneDeep(startProperties.api_input_field_list ?? []))
        mergeUserInputFields(cloneDeep(startProperties.user_input_field_list ?? []))

        const uploadSetting = startProperties.node_data?.file_upload_setting ?? {}
        uploadFields.forEach((field) => syncUploadField(field, Boolean(startProperties.node_data?.file_upload_enable && uploadSetting[field])))
      } else {
        uploadFields.forEach((field) => syncUploadField(field, false))
      }

      model.properties.status = application.id ? 200 : 500
    })
    .catch(() => {
      model.properties.status = 500
    })
}

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  refreshApplicationFields()
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">{{ t('workflow.node.setting') }}</h6>

    <div class="mk-gray-card">
      <el-form
        ref="formRef"
        :model="formData"
        :validate-on-rule-change="false"
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent
      >
        <el-form-item
          :label="t('workflow.start.question')"
          prop="question_reference_address"
          :rules="{ message: t('common.validation.selectFieldRequired', { label: t('workflow.start.question') }), trigger: 'change', required: true }"
        >
          <NodeCascader
            ref="questionCascaderRef"
            v-model="formData.question_reference_address"
            :node-model="model"
            :placeholder="t('common.placeholders.selectField', { label: t('workflow.start.question') })"
          />
        </el-form-item>

        <el-form-item v-if="formData.document_list !== undefined" :label="t('workflow.document.label')" prop="document_list">
          <NodeCascader v-model="formData.document_list" :node-model="model" :placeholder="t('workflow.document.placeholder')" />
        </el-form-item>

        <el-form-item v-if="formData.image_list !== undefined" :label="t('upload.types.image')" prop="image_list">
          <NodeCascader
            v-model="formData.image_list"
            :node-model="model"
            :placeholder="t('common.placeholders.selectField', { label: t('upload.types.image') })"
          />
        </el-form-item>

        <el-form-item v-if="formData.audio_list !== undefined" :label="t('upload.types.audio')" prop="audio_list">
          <NodeCascader
            v-model="formData.audio_list"
            :node-model="model"
            :placeholder="t('common.placeholders.selectField', { label: t('upload.types.audio') })"
          />
        </el-form-item>

        <el-form-item v-if="formData.video_list !== undefined" :label="t('upload.types.video')" prop="video_list">
          <NodeCascader
            v-model="formData.video_list"
            :node-model="model"
            :placeholder="t('common.placeholders.selectField', { label: t('upload.types.video') })"
          />
        </el-form-item>

        <el-form-item
          v-for="(field, index) in formData.api_input_field_list"
          :key="`api-input-${index}`"
          :label="formatFieldLabel(field.variable)"
          :prop="`api_input_field_list.${index}.value`"
          :rules="{
            required: field.is_required,
            message: t('common.validation.selectFieldRequired', { label: formatFieldLabel(field.variable) }),
            trigger: 'change',
          }"
        >
          <NodeCascader v-model="field.value" :node-model="model" :placeholder="t('dynamicForm.fields.parameter.selectPlaceholder')" />
        </el-form-item>

        <el-form-item
          v-for="(field, index) in formData.user_input_field_list"
          :key="`user-input-${index}`"
          :label="formatFieldLabel(field.label)"
          :prop="`user_input_field_list.${index}.value`"
          :rules="{
            required: field.required,
            message: t('common.validation.selectFieldRequired', { label: formatFieldLabel(field.label) }),
            trigger: 'change',
          }"
        >
          <NodeCascader v-model="field.value" :node-model="model" :placeholder="t('dynamicForm.fields.parameter.selectPlaceholder')" />
        </el-form-item>

        <!-- 返回内容 -->
        <div v-if="showReturnContent" class="flex-between w-full">
          <span class="flex-align-center gap-1">
            {{ t('workflow.returnContent.label') }}
            <MkTooltip :content="t('workflow.returnContent.description')" placement="right">
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </MkTooltip>
          </span>
          <el-switch v-model="formData.is_result" size="small" />
        </div>
      </el-form>
    </div>
  </NodeContainer>
</template>
