<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'
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

// 新节点默认不返回内容，旧节点缺少开关时继续按末尾节点兼容。
const defaultForm: ToolLibNodeForm = {
  input_field_list: [],
  is_result: false,
}
const savedForm = model.properties.node_data as Partial<ToolLibNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  input_field_list: Array.isArray(savedForm?.input_field_list) ? savedForm.input_field_list : defaultForm.input_field_list,
  is_result: savedForm ? savedForm.is_result : defaultForm.is_result,
}

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

// 工具参数按名称和来源合并，保留已有引用或自定义值。
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
  if (formData.value.is_result === undefined && isLastNode(model)) formData.value.is_result = true
  refreshToolFields()
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>

    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" hide-required-asterisk @submit.prevent>
        <h6 class="mb-2">输入参数</h6>
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
                <span class="max-w-40 truncate" :class="{ 'mk-required': field.is_required }" :title="field.name">{{ field.name }}</span>
                <el-tooltip v-if="field.desc" :content="field.desc" effect="dark" placement="right">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </el-tooltip>
                <el-tag size="small" type="info">{{ field.type }}</el-tag>
              </div>
            </template>

            <NodeCascader v-if="field.source === 'reference'" v-model="field.value" :node-model="model" placeholder="请选择参数" />
            <el-input v-else v-model="field.value" placeholder="请输入参数" />
          </el-form-item>
        </template>
        <MkEmpty v-else :image-size="60" class="mb-4" />

        <!-- 返回内容 -->
        <div v-if="showReturnContent" class="flex-between w-full">
          <span class="flex items-center gap-1">
            返回内容
            <el-tooltip content="关闭后该节点的内容则不输出给用户。如果你想让用户看到该节点的输出内容，请打开开关。" placement="right">
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </el-tooltip>
          </span>
          <el-switch v-model="formData.is_result" size="small" />
        </div>
      </el-form>
    </div>
  </NodeContainer>
</template>
