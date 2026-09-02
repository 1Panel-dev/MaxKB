<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ToolInputField } from '@/api/types'
import ToolApi from '@/api/admin/workspace/tool/tool'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { isLastNode } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowToolLibNode' })

type ToolNodeInputField =
  | (Omit<ToolInputField, 'source'> & { source: 'reference'; value: string[] })
  | (Omit<ToolInputField, 'source'> & { source: 'custom'; value: string })

interface ToolLibNodeForm {
  input_field_list: ToolNodeInputField[]
  is_result?: boolean
  name?: string
  tool_lib_id?: string
}

const getModel = inject('getModel') as () => WorkflowNodeModel
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

const formRef = useTemplateRef<FormInstance>('formRef')

const toolLibNodeData = (model.properties.node_data ?? {}) as Partial<ToolLibNodeForm>
const shouldInitializeResult = toolLibNodeData.is_result === undefined
if (!Array.isArray(toolLibNodeData.input_field_list)) toolLibNodeData.input_field_list = []
model.properties.node_data = toolLibNodeData as ToolLibNodeForm

const formData = computed<ToolLibNodeForm>({
  get: () => model.properties.node_data as ToolLibNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const showReturnContent = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error })) ?? Promise.resolve()
}

function createInputField(field: ToolInputField, previousFields: ToolNodeInputField[]): ToolNodeInputField {
  const previousField = previousFields.find((item) => item.name === field.name && item.source === field.source)
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

function refreshToolFields() {
  const toolId = formData.value.tool_lib_id
  if (!toolId) {
    model.properties.status = 500
    return
  }

  ToolApi.getToolDetail(toolId)
    .then((tool) => {
      const previousFields = formData.value.input_field_list
      formData.value.name = tool.name
      formData.value.input_field_list = (tool.input_field_list ?? []).map((field) => createInputField(field, previousFields))
      model.properties.status = tool.is_active ? 200 : 500
    })
    .catch(() => {
      model.properties.status = 500
    })
}

onMounted(() => {
  if (shouldInitializeResult) formData.value.is_result = isLastNode(model)
  refreshToolFields()
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mb-3">节点设置</h6>
    <h6 class="mb-2">输入参数</h6>

    <el-form ref="formRef" :model="formData" label-position="top" hide-required-asterisk @submit.prevent>
      <el-card shadow="never" class="card-never mb-4" style="--el-card-padding: 12px">
        <template v-if="formData.input_field_list.length">
          <el-form-item
            v-for="(field, index) in formData.input_field_list"
            :key="`${field.name}-${index}`"
            :prop="`input_field_list.${index}.value`"
            :rules="{
              required: field.is_required,
              message: field.source === 'reference' ? '请选择参数' : '请输入参数',
              trigger: field.source === 'reference' ? 'change' : 'blur',
            }"
          >
            <template #label>
              <div class="flex w-full items-center gap-1">
                <span class="max-w-40 truncate" :title="field.name">{{ field.name }}</span>
                <el-tooltip v-if="field.desc" :content="field.desc" effect="dark" placement="right">
                  <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
                </el-tooltip>
                <span v-if="field.is_required" class="text-danger">*</span>
                <el-tag size="small" type="info">{{ field.type }}</el-tag>
              </div>
            </template>

            <NodeCascader v-if="field.source === 'reference'" v-model="field.value" :node-model="model" class="w-full" placeholder="请选择参数" />
            <el-input v-else v-model="field.value" placeholder="请输入参数" />
          </el-form-item>
        </template>
        <MkEmpty v-else :image-size="60" />
      </el-card>

      <el-form-item v-if="showReturnContent" label="返回内容" @click.prevent>
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
  </NodeContainer>
</template>
