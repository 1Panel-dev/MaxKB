<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import ApplicationApi from '@/api/admin/workspace/application/application'
import { APPLICATION_TYPE } from '@/api/enums'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowApplicationNode' })

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
const model = getModel()

const formRef = useTemplateRef<FormInstance>('formRef')
const questionCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('questionCascaderRef')

const applicationNodeData = (model.properties.node_data ?? {}) as Partial<ApplicationNodeForm>
if (!Array.isArray(applicationNodeData.question_reference_address)) {
  applicationNodeData.question_reference_address = [WorkflowNodeType.Start, 'question']
}
if (!Array.isArray(applicationNodeData.api_input_field_list)) applicationNodeData.api_input_field_list = []
if (!Array.isArray(applicationNodeData.user_input_field_list)) applicationNodeData.user_input_field_list = []
if (applicationNodeData.is_result === undefined) applicationNodeData.is_result = false
model.properties.node_data = applicationNodeData as ApplicationNodeForm

const formData = computed<ApplicationNodeForm>({
  get: () => model.properties.node_data as ApplicationNodeForm,
  set: (value) => (model.properties.node_data = value),
})

function formatFieldLabel(label: FieldLabel) {
  return typeof label === 'object' && label !== null ? (label.label ?? '') : label
}

function validate() {
  return Promise.all([questionCascaderRef.value?.validate(), formRef.value?.validate()]).catch((error) =>
    Promise.reject({ node: model, errMessage: error }),
  )
}

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

onMounted(() => {
  refreshApplicationFields()
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mb-3">节点设置</h6>

    <el-card shadow="never" class="card-never">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item label="用户问题" prop="question_reference_address" :rules="{ message: '请选择用户问题', trigger: 'change', required: true }">
          <NodeCascader
            ref="questionCascaderRef"
            v-model="formData.question_reference_address"
            :node-model="model"
            class="w-full"
            placeholder="请选择用户问题"
          />
        </el-form-item>

        <el-form-item v-if="formData.document_list !== undefined" label="选择文档" prop="document_list">
          <NodeCascader v-model="formData.document_list" :node-model="model" class="w-full" placeholder="请选择文档" />
        </el-form-item>

        <el-form-item v-if="formData.image_list !== undefined" label="选择图片" prop="image_list">
          <NodeCascader v-model="formData.image_list" :node-model="model" class="w-full" placeholder="请选择图片" />
        </el-form-item>

        <el-form-item v-if="formData.audio_list !== undefined" label="选择音频" prop="audio_list">
          <NodeCascader v-model="formData.audio_list" :node-model="model" class="w-full" placeholder="请选择音频" />
        </el-form-item>

        <el-form-item v-if="formData.video_list !== undefined" label="选择视频" prop="video_list">
          <NodeCascader v-model="formData.video_list" :node-model="model" class="w-full" placeholder="请选择视频" />
        </el-form-item>

        <el-form-item
          v-for="(field, index) in formData.api_input_field_list"
          :key="`api-input-${index}`"
          :label="formatFieldLabel(field.variable)"
          :prop="`api_input_field_list.${index}.value`"
          :rules="{ required: field.is_required, message: `请选择${formatFieldLabel(field.variable)}`, trigger: 'change' }"
        >
          <NodeCascader v-model="field.value" :node-model="model" class="w-full" placeholder="请选择参数" />
        </el-form-item>

        <el-form-item
          v-for="(field, index) in formData.user_input_field_list"
          :key="`user-input-${index}`"
          :label="formatFieldLabel(field.label)"
          :prop="`user_input_field_list.${index}.value`"
          :rules="{ required: field.required, message: `请选择${formatFieldLabel(field.label)}`, trigger: 'change' }"
        >
          <NodeCascader v-model="field.value" :node-model="model" class="w-full" placeholder="请选择参数" />
        </el-form-item>

        <el-form-item label="返回内容" @click.prevent>
          <template #label>
            <div class="flex items-center gap-1">
              <span>返回内容</span>
              <el-tooltip content="开启后，该节点的输出会作为工作流的最终回复内容" effect="dark" placement="right">
                <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
              </el-tooltip>
            </div>
          </template>
          <el-switch v-model="formData.is_result" size="small" />
        </el-form-item>
      </el-form>
    </el-card>
  </NodeContainer>
</template>
