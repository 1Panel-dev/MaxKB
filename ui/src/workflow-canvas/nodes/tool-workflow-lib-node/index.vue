<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'
import { cloneDeep, set } from 'lodash'
import type { FormInstance } from 'element-plus'
import ToolApi from '@/api/admin/workspace/tool/tool'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowToolWorkflowLibNode' })

interface InputField {
  field: string
  label: string
  name?: string
  type: string
  is_required?: boolean
  source: 'reference' | 'custom'
  value: any
}

interface OutputField {
  label: string
  value: string
}

interface ToolWorkflowLibNodeForm {
  input_field_list: InputField[]
  input_title?: string
  is_result?: boolean
  tool_lib_id?: string
}

const getModel = inject('getModel') as () => WorkflowNodeModel
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

const formRef = useTemplateRef<FormInstance>('formRef')

const toolNodeData = (model.properties.node_data ?? {}) as Partial<ToolWorkflowLibNodeForm>
if (!Array.isArray(toolNodeData.input_field_list)) toolNodeData.input_field_list = []
model.properties.node_data = toolNodeData as ToolWorkflowLibNodeForm

const formData = computed<ToolWorkflowLibNodeForm>({
  get: () => model.properties.node_data as ToolWorkflowLibNodeForm,
  set: (value) => set(model.properties, 'node_data', value),
})

const showReturnContent = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

const inputTitle = computed(() => formData.value.input_title || '输入参数')

function onSourceChange(item: InputField) {
  if (item.type === 'boolean') {
    item.value = false
  } else if (['array', 'dict'].includes(item.type)) {
    item.value = []
  } else {
    item.value = ''
  }
}

function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error })) ?? Promise.resolve()
}

function createInputField(field: InputField, previousFields: InputField[]): InputField {
  const previousField = previousFields.find((item) => item.field === field.field)
  if (field.source === 'reference') {
    return {
      ...field,
      source: 'reference',
      value: previousField?.source === 'reference' ? cloneDeep(previousField.value) : [],
    }
  }
  return {
    ...field,
    source: 'custom',
    value: previousField?.source === 'custom' ? previousField.value : '',
  }
}

function updateField() {
  const toolId = formData.value.tool_lib_id
  if (!toolId) {
    model.properties.status = 500
    return
  }

  ToolApi.getToolDetail(toolId)
    .then((tool) => {
      const workflowNodes = (tool as any)?.work_flow?.nodes || []
      const baseNode = workflowNodes.find((n: any) => n.type === 'tool-base-node')

      if (baseNode) {
        const newInputList = baseNode.properties.user_input_field_list || []
        const newOutputList = baseNode.properties.user_output_field_list || []

        const oldConfigFields = (model.properties.config?.fields || []) as OutputField[]
        const configFieldList = newOutputList.map((item: any) => {
          const old = oldConfigFields.find((o) => o.value === item.field)
          return old ? JSON.parse(JSON.stringify(old)) : { label: item.label, value: item.field }
        })

        const inputTitleValue = baseNode.properties.user_input_config?.title
        const outputTitle = baseNode.properties.user_output_config?.title
        const previousFields = formData.value.input_field_list
        const mergedInputList = newInputList.map((item: any) => {
          const findField = previousFields.find((oldItem) => oldItem.field === item.field)
          if (findField) {
            return {
              ...item,
              source: findField.source,
              value: JSON.parse(JSON.stringify(findField.value)),
            }
          }
          return { ...item, source: 'custom', value: '' }
        })

        set(formData.value, 'input_field_list', mergedInputList)
        set(model.properties, 'config', {
          fields: configFieldList,
          output_title: outputTitle,
        })
        set(formData.value, 'input_title', inputTitleValue)
      }
      model.properties.status = (tool as any)?.is_active ? 200 : 500
      model.clearNextNodeField(true)
    })
    .catch(() => {
      model.properties.status = 500
    })
}

onMounted(() => {
  if (typeof formData.value.is_result === 'undefined') {
    const isLast = !model.graphModel.getNodeOutgoingNode(model.id).length
    if (isLast) {
      formData.value.is_result = true
    }
  }
  updateField()
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <el-form ref="formRef" :model="formData" label-position="top" hide-required-asterisk @submit.prevent>
      <h6 class="mk-title-decoration mb-2">{{ inputTitle }}</h6>

      <el-card shadow="never" class="card-never mb-4" style="--el-card-padding: 12px">
        <template v-if="formData.input_field_list.length">
          <el-form-item
            v-for="(field, index) in formData.input_field_list"
            :key="`${field.field}-${index}`"
            :prop="`input_field_list.${index}.value`"
            :rules="{
              required: field.is_required,
              message: field.source === 'reference' ? '请选择参数' : '请输入参数',
              trigger: field.source === 'reference' ? 'change' : 'blur',
            }"
          >
            <template #label>
              <div class="flex-between">
                <div class="flex items-center">
                  <div class="mr-2 max-w-32 truncate" :title="field.label">
                    {{ field.label }}
                  </div>
                  <span v-if="field.is_required" class="text-danger">*</span>
                </div>
                <el-select
                  :teleported="false"
                  v-model="field.source"
                  @change="onSourceChange(field)"
                  size="small"
                  style="width: 85px"
                >
                  <el-option label="引用" value="reference" />
                  <el-option label="自定义" value="custom" />
                </el-select>
              </div>
            </template>
            <NodeCascader
              v-if="field.source === 'reference'"
              v-model="field.value"
              :node-model="model"
              class="w-full"
              placeholder="请选择参数"
            />
            <template v-else>
              <el-input
                v-if="['string'].includes(field.type)"
                v-model="field.value"
                placeholder="请输入参数"
              />
              <el-input-number
                v-if="['int', 'float'].includes(field.type)"
                v-model="field.value"
                class="w-full"
              />
              <el-switch
                v-if="['boolean'].includes(field.type)"
                v-model="field.value"
                :active-value="true"
                :inactive-value="false"
              />
            </template>
          </el-form-item>
        </template>
        <MkEmpty v-else :image-size="60" />
      </el-card>

      <el-form-item v-if="showReturnContent" label="返回内容" @click.prevent>
        <template #label>
          <div class="flex items-center gap-1">
            <span>返回内容</span>
            <el-tooltip content="开启后，该节点的输出会作为工作流的最终回复内容" effect="dark" placement="right">
              <MkIcon name="icon_help_outlined" class="cursor-help text-N600" />
            </el-tooltip>
          </div>
        </template>
        <el-switch v-model="formData.is_result" size="small" />
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>