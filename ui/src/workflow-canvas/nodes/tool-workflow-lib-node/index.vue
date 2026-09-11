<script setup lang="ts">
import { computed, inject, nextTick, onBeforeUnmount, onMounted, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import JsonInput from '@/components/codemirror-editor/Json.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import { createAnchorGuard, handleNodeWheel } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode, WorkflowNodeType } from '@/workflow-canvas/types'
import type { ToolFieldConfig, ToolInputField, ToolOutputField } from '../tool-base-node/types'

defineOptions({ name: 'WorkflowToolWorkflowLibNode' })

type WorkflowToolInputField = ToolInputField & ({ source: 'reference'; value: string[] } | { source: 'custom'; value: unknown })

interface ToolWorkflowLibNodeForm {
  input_field_list: WorkflowToolInputField[]
  input_title?: string
  is_result?: boolean
  tool_lib_id?: string
}

interface ToolBaseProperties {
  user_input_field_list?: ToolInputField[]
  user_output_field_list?: ToolOutputField[]
  user_input_config?: ToolFieldConfig
  user_output_config?: ToolFieldConfig
}

const getModel = inject<() => WorkflowNodeModel>('getModel')!
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const store = useWorkflowStore(inject<string>('apiType', 'workspace'))
const model = getModel()
const formRef = useTemplateRef<FormInstance>('formRef')
const anchorGuard = createAnchorGuard(model)
let disposed = false

// 保留旧节点缺少返回内容开关时，无后继节点即开启的兼容逻辑。
const defaultForm: ToolWorkflowLibNodeForm = { input_field_list: [] }
const savedForm = model.properties.node_data as Partial<ToolWorkflowLibNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  input_field_list: Array.isArray(savedForm?.input_field_list) ? savedForm.input_field_list : defaultForm.input_field_list,
}
const formData = computed({
  get: () => model.properties.node_data as ToolWorkflowLibNodeForm,
  set: (value: ToolWorkflowLibNodeForm) => (model.properties.node_data = value),
})
const inputTitle = computed(() => formData.value.input_title || '输入参数')
const showReturnContent = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

// 切换来源时引用统一为空路径，自定义值按参数类型初始化。
function getCustomValue(type: string): unknown {
  if (type === 'boolean') return false
  if (type === 'array') return []
  if (type === 'dict') return {}
  if (type === 'int' || type === 'float') return undefined
  return ''
}

function changeSource(field: WorkflowToolInputField, source: 'reference' | 'custom', index: number) {
  const inputFields = cloneDeep(formData.value.input_field_list)
  inputFields[index] = source === 'reference' ? { ...field, source, value: [] } : { ...field, source, value: getCustomValue(field.type) }
  formData.value = { ...formData.value, input_field_list: inputFields }
  void nextTick(() => formRef.value?.clearValidate(`input_field_list.${index}.value`))
}

// 按字段标识保留用户值和来源，同时更新工具定义中的名称、类型与输出字段。
function refreshToolFields() {
  const toolId = formData.value.tool_lib_id
  if (!toolId) {
    model.properties.status = 500
    return
  }
  store.force
    .getToolById(toolId)
    .then((tool) => {
      if (disposed || formData.value.tool_lib_id !== toolId) return
      const baseNode = tool.work_flow?.nodes?.find((node) => node.type === WorkflowNodeType.ToolBaseNode)
      if (!baseNode) {
        model.properties.status = 500
        return
      }
      const properties = (baseNode.properties ?? {}) as ToolBaseProperties
      const previousInputs = new Map(formData.value.input_field_list.map((field) => [field.field, field]))
      const previousOutputs = new Map(model.properties.config?.fields?.map((field) => [field.value, field]))
      const inputFields = (properties.user_input_field_list ?? []).map((field): WorkflowToolInputField => {
        const previousField = previousInputs.get(field.field)
        if (previousField?.source === 'reference')
          return { ...field, source: 'reference', value: Array.isArray(previousField.value) ? cloneDeep(previousField.value) : [] }
        return { ...field, source: 'custom', value: previousField ? cloneDeep(previousField.value) : getCustomValue(field.type) }
      })
      const outputFields = (properties.user_output_field_list ?? []).map((field) => ({
        ...cloneDeep(previousOutputs.get(field.field)),
        label: field.label || field.name || field.field,
        value: field.field,
      }))
      formData.value = { ...formData.value, input_field_list: inputFields, input_title: properties.user_input_config?.title }
      const nodeConfig = { ...model.properties.config, fields: outputFields, output_title: properties.user_output_config?.title }
      model.properties.config = nodeConfig
      model.properties.status = tool.is_active ? 200 : 500
      model.clearNextNodeField(true)
    })
    .catch(() => {
      if (!disposed && formData.value.tool_lib_id === toolId) model.properties.status = 500
    })
}

// 节点统一调用表单校验，输入组件负责触发表单项校验。
function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error })) ?? Promise.resolve()
}

onMounted(() => {
  if (formData.value.is_result === undefined && !model.graphModel.getNodeOutgoingNode(model.id).length) formData.value.is_result = true
  refreshToolFields()
  model.validate = validate
})
onBeforeUnmount(() => {
  disposed = true
  anchorGuard.reset()
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" hide-required-asterisk @submit.prevent>
        <h6 class="mb-2">{{ inputTitle }}</h6>
        <div v-if="formData.input_field_list.length" class="mk-white-card">
          <template v-for="(field, index) in formData.input_field_list" :key="field.field">
            <el-form-item
              :prop="`input_field_list.${index}.value`"
              :rules="{
                required: field.is_required,
                message: field.source === 'reference' ? '请选择参数' : '请输入参数',
                trigger: field.source === 'reference' ? 'change' : 'blur',
              }"
            >
              <template #label>
                <div class="flex-between w-full gap-2">
                  <div class="flex min-w-0 items-center gap-1">
                    <span class="max-w-32 truncate" :class="{ 'mk-required': field.is_required }" :title="field.label || field.name || field.field">
                      {{ field.label || field.name || field.field }}
                    </span>
                    <el-tooltip v-if="field.desc" :content="field.desc" placement="right">
                      <MkIcon name="icon_info_outlined" class="text-N600!" />
                    </el-tooltip>
                    <el-tag size="small" type="info">{{ field.type }}</el-tag>
                  </div>
                  <el-select
                    :model-value="field.source"
                    :teleported="false"
                    size="small"
                    class="w-22! shrink-0"
                    @change="changeSource(field, $event, index)"
                    @visible-change="anchorGuard.setOverlayVisible(field.field, $event)"
                  >
                    <el-option label="引用" value="reference" />
                    <el-option label="自定义" value="custom" />
                  </el-select>
                </div>
              </template>
              <NodeCascader v-if="field.source === 'reference'" v-model="field.value" :node-model="model" placeholder="请选择参数" />
              <template v-else>
                <el-switch v-if="field.type === 'boolean'" :model-value="field.value" size="small" @update:model-value="field.value = $event" />
                <el-input-number
                  v-else-if="field.type === 'int' || field.type === 'float'"
                  :model-value="field.value"
                  :precision="field.type === 'int' ? 0 : undefined"
                  class="w-full!"
                  controls-position="right"
                  @update:model-value="field.value = $event"
                />
                <JsonInput v-else-if="field.type === 'array' || field.type === 'dict'" v-model="field.value" @wheel="handleNodeWheel" />
                <el-input v-else :model-value="field.value" placeholder="请输入参数" @update:model-value="field.value = $event" />
              </template>
            </el-form-item>
          </template>
        </div>
        <span v-else>暂无数据</span>

        <!-- 返回内容 -->
        <div v-if="showReturnContent" class="flex-between mt-4 w-full">
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
