<template>
  <NodeContainer :node-model="model">
    <h6 class="mb-3">节点设置</h6>
    <div class="border-r-6 layout-bg lighter mb-8 p-8-12">
      <el-form
        ref="mcpNodeFormRef"
        :model="form_data"
        label-position="top"
        require-asterisk-position="right"
        label-width="auto"
        hide-required-asterisk
        @submit.prevent
      >
        <el-form-item label="MCP Server Config">
          <template #label>
            <div class="flex-between">
              <div>MCP Server Config<span class="text-danger">*</span></div>
              <el-select :teleported="false" v-model="form_data.mcp_source" size="small" style="width: 85px">
                <el-option label="引用变量" value="referencing" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </div>
          </template>
          <MdEditorMagnify
            v-if="form_data.mcp_source === 'custom'"
            title="MCP Server Config"
            v-model="form_data.mcp_servers"
            style="height: 150px"
            :placeholder="mcpServerJson"
            @wheel="handleNodeWheel"
          />
          <el-select v-else :teleported="false" v-model="form_data.mcp_tool_id" filterable @change="mcpToolSelectChange" @wheel="handleNodeWheel">
            <el-option v-for="mcpTool in mcpToolSelectOptions" :key="mcpTool.id" :label="mcpTool.name" :value="mcpTool.id">
              <div class="flex items-center">
                <ToolIcon v-if="!mcpTool.icon" :size="20" :type="mcpTool.tool_type" class="mr-2" />
                <el-avatar v-else shape="square" :size="20" class="mr-2" style="background: none">
                  <img :src="mcpTool.icon" alt="" />
                </el-avatar>
                <span>{{ mcpTool.name }}</span>
                <el-tag v-if="mcpTool.scope === 'SHARED'" size="small" type="info" class="info-tag ml-2">共享</el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <span>工具</span>
              <el-button type="primary" link @click="getTools">
                <MkIcon name="icon_add_outlined" class="mr-1" />
                获取工具
              </el-button>
            </div>
          </template>
          <el-select v-model="form_data.mcp_tool" filterable :teleported="false" @change="changeTool" @wheel="handleNodeWheel">
            <el-option v-for="item in form_data.mcp_tools" :key="item.name" :label="item.name" :value="item.name" class="flex items-center">
              <el-tooltip effect="dark" :content="item.description" placement="top-start" popper-class="max-w-350">
                <MkIcon name="icon_warning_filled" />
              </el-tooltip>
              <span class="ml-4">{{ item.name }}</span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
    </div>
    <h6 class="mb-3">工具参数</h6>
    <div v-if="form_data.mcp_tool" class="border-r-6 layout-bg lighter p-8-12">
      <el-form
        ref="dynamicsFormRef"
        label-position="top"
        v-loading="loading"
        require-asterisk-position="right"
        :hide-required-asterisk="true"
        @submit.prevent
      >
        <el-form-item v-for="item in form_data.tool_form_field" :key="item.field" :required="item.required">
          <template #label>
            <div class="flex-between">
              <div>
                <TooltipLabel v-if="item.label.attrs?.tooltip" :label="item.label" :required="item.required" />
                <span v-else>{{ item.label.label }}</span>
                <span v-if="item.required" class="text-danger">*</span>
              </div>
              <el-select :teleported="false" v-model="item.source" size="small" style="width: 85px" @change="setParamValue(item, '')">
                <el-option label="引用变量" value="referencing" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </div>
          </template>
          <el-input
            v-if="item.source === 'custom' && item.input_type === 'TextInput'"
            :model-value="paramsOf()[item.label.label]"
            @update:model-value="setParamValue(item, $event)"
          />
          <el-input-number
            v-else-if="item.source === 'custom' && item.input_type === 'NumberInput'"
            :model-value="paramsOf()[item.label.label]"
            @update:model-value="setParamValue(item, $event)"
          />
          <el-switch
            v-else-if="item.source === 'custom' && item.input_type === 'SwitchInput'"
            :model-value="paramsOf()[item.label.label]"
            @update:model-value="setParamValue(item, $event)"
          />
          <el-input
            v-else-if="item.source === 'custom' && item.input_type === 'JsonInput'"
            :model-value="paramsOf()[item.label.label]"
            @update:model-value="setParamValue(item, $event)"
            type="textarea"
          />
          <NodeCascader
            v-if="item.source === 'referencing'"
            :ref="setCascaderRef"
            :node-model="model"
            class="w-full"
            placeholder="请选择变量"
            :model-value="paramsOf()[item.label.label] as string[]"
            @update:model-value="setParamValue(item, $event)"
          />
        </el-form-item>
      </el-form>
    </div>
    <div v-else class="border-r-6 layout-bg lighter p-8-12">
      <el-text type="info">暂无数据</el-text>
    </div>
    <McpServerInputDialog ref="mcpServerInputDialogRef" @refresh="handleMcpVariables" />
  </NodeContainer>
</template>
<script setup lang="ts">
import { TOOL_TYPE } from '@/api/enums'
import { computed, inject, onMounted, ref, type Ref, useTemplateRef } from 'vue'
import { set } from 'lodash'
import type { BaseNodeModel } from '@logicflow/core'
import type { FormInstance } from 'element-plus'
import { useRoute } from 'vue-router'

import McpServerInputDialog from './component/McpServerInputDialog.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import { useWorkflowStore } from '@/workflow-canvas/store'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { WorkflowMode } from '@/workflow-canvas/types'
import type { ToolItem } from '@/api/types'
import TooltipLabel from '@/components/mk-dynamics-form/items/label/TooltipLabel.vue'
import type { FormFieldLabel } from '@/components/mk-dynamics-form/type'
import { MsgError, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'WorkflowMcpNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel() as WorkflowNodeModel
const route = useRoute()

const MCP_RESOURCE = {
  [WorkflowMode.Application]: { type: 'application', id: () => route.params.applicationId as string },
  [WorkflowMode.ApplicationLoop]: { type: 'application', id: () => route.params.applicationId as string },
  [WorkflowMode.Tool]: { type: 'tool', id: () => route.params.toolId as string },
  [WorkflowMode.ToolLoop]: { type: 'tool', id: () => route.params.toolId as string },
  [WorkflowMode.Knowledge]: { type: 'knowledge', id: () => route.params.knowledgeId as string },
  [WorkflowMode.KnowledgeLoop]: { type: 'knowledge', id: () => route.params.knowledgeId as string },
} as const
const mcpResource = MCP_RESOURCE[workflowMode] ?? MCP_RESOURCE[WorkflowMode.Application]
const mcpResourceType = mcpResource.type
const mcpResourceId = mcpResource.id() || ''

const store = useWorkflowStore(apiType)

interface SchemaProperty {
  description?: string
  properties?: Record<string, SchemaProperty>
  type?: string
}
interface ArgsSchema {
  properties?: Record<string, SchemaProperty & { required?: string[] }>
  required?: string[]
}

interface ToolFormFieldItem {
  field: string
  label: FormFieldLabel & { label: string; attrs?: { tooltip?: string } }
  input_type: string
  source: 'referencing' | 'custom'
  required: boolean
}

interface McpNodeData {
  is_result?: boolean
  mcp_tool: string
  mcp_tools: Array<{ name: string; server: string; description: string; args_schema?: ArgsSchema }>
  mcp_servers: string
  mcp_server: string
  mcp_source: string
  mcp_tool_id: string
  tool_params: Record<string, unknown>
  tool_form_field: ToolFormFieldItem[]
  params_nested: string
}

const mcpServerJson = `{
  "math": {
    "url": "your_server",
    "transport": "sse"
  }
}`

const defaultForm = (): McpNodeData => ({
  mcp_tool: '',
  mcp_tools: [],
  mcp_servers: '',
  mcp_server: '',
  mcp_source: 'referencing',
  mcp_tool_id: '',
  tool_params: {},
  tool_form_field: [],
  params_nested: '',
})

if (!model.properties.node_data) {
  set(model.properties, 'node_data', defaultForm())
}
const initialData = model.properties.node_data as McpNodeData
if (initialData.mcp_servers && !initialData.mcp_source) {
  set(initialData, 'mcp_source', 'custom')
}
const form_data = computed<McpNodeData>({
  get: () => model.properties.node_data as McpNodeData,
  set: (value) => {
    set(model.properties, 'node_data', value)
  },
})

const mcpNodeFormRef = useTemplateRef<FormInstance>('mcpNodeFormRef')
const dynamicsFormRef = useTemplateRef<FormInstance>('dynamicsFormRef')
const mcpServerInputDialogRef = useTemplateRef<InstanceType<typeof McpServerInputDialog>>('mcpServerInputDialogRef')
const nodeCascaderRef: Ref<Array<{ validate: () => Promise<unknown> }>> = ref([])
const loading = ref(false)
const mcpToolSelectOptions = ref<ToolItem[]>([])

function setCascaderRef(el: unknown) {
  if (el && !nodeCascaderRef.value.includes(el as { validate: () => Promise<unknown> })) {
    nodeCascaderRef.value.push(el as { validate: () => Promise<unknown> })
  }
}

function paramsOf(): Record<string, unknown> {
  const params = form_data.value.tool_params
  if (form_data.value.params_nested) {
    return (params[form_data.value.params_nested] as Record<string, unknown>) ?? {}
  }
  return params
}

function setParamValue(item: ToolFormFieldItem, value: unknown) {
  const params = form_data.value.tool_params
  if (form_data.value.params_nested) {
    const nested = (params[form_data.value.params_nested] as Record<string, unknown>) ?? {}
    nested[item.label.label] = value
    params[form_data.value.params_nested] = nested
  } else {
    params[item.label.label] = value
  }
  set(form_data.value, 'tool_params', params)
}

async function mcpToolSelectChange() {
  const tool = await store.getToolById(form_data.value.mcp_tool_id)
  form_data.value.mcp_servers = tool?.code ?? ''
}

function getTools() {
  if (form_data.value.mcp_source === 'referencing' && !form_data.value.mcp_tool_id) {
    MsgError('请先选择引用的 MCP 工具')
    return
  }
  if (form_data.value.mcp_source === 'referencing' && form_data.value.mcp_tool_id) {
    if (!mcpToolSelectOptions.value.find((item) => item.id === form_data.value.mcp_tool_id)) {
      MsgError('请先选择引用的 MCP 工具')
      return
    }
  }
  if (form_data.value.mcp_source === 'custom' && !form_data.value.mcp_servers) {
    MsgError('请先配置 MCP Server')
    return
  }
  try {
    JSON.parse(form_data.value.mcp_servers)
    const vars = extractPlaceholders(form_data.value.mcp_servers)
    if (vars.length > 0) {
      mcpServerInputDialogRef.value?.open(vars)
      return
    }
  } catch {
    MsgError('请先配置 MCP Server')
    return
  }
  _getTools(form_data.value.mcp_servers)
}

async function _getTools(mcpServers: string) {
  loading.value = true
  try {
    const tools = await store.getMcpTools(mcpResourceType, mcpResourceId, mcpServers)
    form_data.value.mcp_tools = tools
    MsgSuccess('获取工具成功')
    form_data.value.mcp_server = tools.find((item) => item.name === form_data.value.mcp_tool)?.server ?? ''
  } catch {
    MsgError('获取工具失败，请检查 MCP Server 配置')
  } finally {
    loading.value = false
  }
}

function extractPlaceholders(input: unknown): string[] {
  const re = /\{\{\s*([a-zA-Z_][\w.]*)\s*\}\}/g
  const found = new Set<string>()

  const visit = (v: unknown) => {
    if (typeof v === 'string') {
      let m: RegExpExecArray | null
      while ((m = re.exec(v)) !== null) {
        if (m[1]) found.add(m[1])
      }
    } else if (Array.isArray(v)) {
      v.forEach(visit)
    } else if (v && typeof v === 'object') {
      Object.values(v as Record<string, unknown>).forEach(visit)
    }
  }

  if (typeof input === 'string') {
    try {
      visit(JSON.parse(input))
    } catch {
      visit(input)
    }
  } else {
    visit(input)
  }

  return [...found]
}

function handleMcpVariables(vars: Record<string, string>) {
  let mcpServers = form_data.value.mcp_servers
  for (const item in vars) {
    const value = vars[item]
    if (value !== undefined) mcpServers = mcpServers.replace(`{{${item}}}`, value)
  }
  _getTools(mcpServers)
}

function changeTool() {
  const selected = form_data.value.mcp_tools.find((item) => item.name === form_data.value.mcp_tool)
  form_data.value.mcp_server = selected?.server ?? ''
  const argsSchema = selected?.args_schema as ArgsSchema | undefined
  form_data.value.tool_form_field = []

  const resolveInputType = (type?: string): string => {
    if (type === 'number') return 'NumberInput'
    if (type === 'boolean') return 'SwitchInput'
    if (['array', 'object'].includes(type ?? '')) return 'JsonInput'
    return 'TextInput'
  }

  for (const item in argsSchema?.properties) {
    const property = argsSchema.properties[item] as SchemaProperty & { required?: string[] }
    const nested = property.properties
    const input_type = resolveInputType(property.type)

    if (nested) {
      form_data.value.params_nested = item
      for (const item2 in nested) {
        const nestedProp = nested[item2]
        form_data.value.tool_form_field.push({
          field: item2,
          label: { input_type: 'TooltipLabel', label: item2, attrs: { tooltip: nestedProp?.description } },
          input_type: resolveInputType(nestedProp?.type),
          source: 'referencing',
          required: property.required?.indexOf(item2) !== -1,
        })
      }
    } else {
      form_data.value.params_nested = ''
      form_data.value.tool_form_field.push({
        field: item,
        label: { input_type: 'TooltipLabel', label: item, attrs: { tooltip: property.description } },
        input_type,
        source: 'referencing',
        required: argsSchema.required?.indexOf(item) !== -1,
      })
    }
  }
  if (form_data.value.params_nested) {
    form_data.value.tool_params = { [form_data.value.params_nested]: {} }
  } else {
    form_data.value.tool_params = {}
  }
}

const validate = () => {
  const vList: Array<Promise<unknown>> = []
  const requiredFields = (form_data.value.tool_form_field || []).filter((item) => item.required)
  if (requiredFields.length > 0) {
    for (const item of requiredFields) {
      const value = paramsOf()[item.label.label]
      if (value === undefined || value === null || value === '') {
        vList.push(Promise.reject(`${item.label.label} 为必填项`))
      }
    }
  }
  if (dynamicsFormRef.value || mcpNodeFormRef.value) {
    if (!form_data.value.mcp_servers) vList.push(Promise.reject('请先配置 MCP Server'))
    if (!form_data.value.mcp_tool) vList.push(Promise.reject('请选择 MCP 工具'))
  }
  const cascaderResults = nodeCascaderRef.value.map((item) => item.validate())
  return Promise.all([...vList, ...cascaderResults]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

async function getMcpToolSelectOptions() {
  const tools = await store.getToolListWithShared({ tool_type: TOOL_TYPE.MCP })
  mcpToolSelectOptions.value = tools.filter((item) => item.is_active)
}

onMounted(() => {
  if (form_data.value.is_result === undefined && isLastNode(model)) {
    set(form_data.value, 'is_result', true)
  }
  set(model, 'validate', validate)
  getMcpToolSelectOptions()
})
</script>
<style lang="scss" scoped>
:deep(.app-warning-icon) {
  color: var(--el-color-primary-light-5);

  &:hover {
    color: var(--el-color-primary-light-3);
  }
}
</style>
