<script setup lang="ts">
import { computed, inject, nextTick, onMounted, ref, useTemplateRef } from 'vue'
import { useRoute } from 'vue-router'
import { set } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ToolItem } from '@/api/types'
import type { FormFieldLabel } from '@/components/mk-dynamics-form/type'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { BaseNodeModel } from '@logicflow/core'
import type { FormInstance } from 'element-plus'
import type { Ref } from 'vue'
import { TOOL_TYPE } from '@/api/enums'
import TooltipLabel from '@/components/mk-dynamics-form/items/label/TooltipLabel.vue'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'
import McpServerInputDialog from './component/McpServerInputDialog.vue'
import { MsgError, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'WorkflowMcpNode' })
const { t } = useI18n({ useScope: 'global' })
const getModel = inject('getModel') as () => BaseNodeModel
const resourceScope = (inject('resourceScope') as string) || 'workspace'
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

const resourceWorkspaceId = inject<Ref<string | null | undefined>>('resourceWorkspaceId', ref())
const store = useWorkflowStore(resourceScope, () => resourceWorkspaceId.value)

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
const loading = ref(false)
const mcpToolSelectOptions = ref<ToolItem[]>([])
const mcpConfigProp = computed(() => (form_data.value.mcp_source === 'custom' ? 'mcp_servers' : 'mcp_tool_id'))

function changeMcpSource() {
  nextTick(() => mcpNodeFormRef.value?.clearValidate(['mcp_servers', 'mcp_tool_id']))
}

function paramsOf(): Record<string, unknown> {
  const params = form_data.value.tool_params
  if (form_data.value.params_nested) {
    return (params[form_data.value.params_nested] as Record<string, unknown>) ?? {}
  }
  return params
}

// 引用参数只向级联选择器传入字符串路径，未填写或旧的非路径值按空选项展示。
function getParamReference(item: ToolFormFieldItem): string[] {
  const value = paramsOf()[item.label.label]
  return Array.isArray(value) && value.every((segment): segment is string => typeof segment === 'string') ? value : []
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

async function getTools() {
  const valid = await mcpNodeFormRef.value?.validateField(mcpConfigProp.value).catch(() => false)
  if (!valid) return
  if (form_data.value.mcp_source === 'referencing' && form_data.value.mcp_tool_id) {
    if (!mcpToolSelectOptions.value.find((item) => item.id === form_data.value.mcp_tool_id)) {
      MsgError(t('workflow.mcp.reference.requiredMessage'))
      return
    }
  }
  try {
    JSON.parse(form_data.value.mcp_servers)
    const vars = extractPlaceholders(form_data.value.mcp_servers)
    if (vars.length > 0) {
      mcpServerInputDialogRef.value?.open(vars)
      return
    }
  } catch {
    MsgError(t('workflow.mcp.serverConfig.requiredMessage'))
    return
  }
  _getTools(form_data.value.mcp_servers)
}

async function _getTools(mcpServers: string) {
  loading.value = true
  try {
    const tools = await store.force.getMcpTools(mcpResourceType, mcpResourceId, mcpServers)
    form_data.value.mcp_tools = tools
    const selected = tools.find((tool) => tool.name === form_data.value.mcp_tool)
    if (selected?.args_schema) {
      const previousFields = form_data.value.tool_form_field ?? []
      const previousParams = paramsOf() ?? {}
      const previousNested = form_data.value.params_nested ?? ''
      changeTool()
      if (previousNested === form_data.value.params_nested) {
        const params = paramsOf()
        for (const field of form_data.value.tool_form_field) {
          const previous = previousFields.find((item) => item.field === field.field && item.input_type === field.input_type)
          if (!previous) continue
          field.source = previous.source
          if (Object.hasOwn(previousParams, field.field)) params[field.field] = previousParams[field.field]
        }
      }
    }
    MsgSuccess(t('workflow.mcp.tools.loadSuccess'))
    form_data.value.mcp_server = selected?.server ?? ''
  } catch {
    MsgError(t('workflow.mcp.tools.loadFailed'))
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
  form_data.value.params_nested = ''

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
        vList.push(Promise.reject(t('common.validation.inputFieldRequired', { label: item.label.label })))
      }
    }
  }
  if (dynamicsFormRef.value || mcpNodeFormRef.value) {
    if (!form_data.value.mcp_tool) vList.push(Promise.reject(t('tool.mcp.tools.requiredMessage')))
  }
  if (mcpNodeFormRef.value) vList.push(mcpNodeFormRef.value.validate())
  return Promise.all([...vList]).catch((error) => Promise.reject({ node: model, errMessage: error }))
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
<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">{{ t('workflow.node.setting') }}</h6>
    <div class="mk-gray-card">
      <el-form
        ref="mcpNodeFormRef"
        :model="form_data"
        :validate-on-rule-change="false"
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent
      >
        <!-- MCP Server Config -->
        <el-form-item
          :label="t('workflow.mcp.serverConfig.label')"
          :prop="mcpConfigProp"
          class="mk-hide-asterisk"
          :rules="[
            {
              required: true,
              message:
                form_data.mcp_source === 'custom' ? t('workflow.mcp.serverConfig.requiredMessage') : t('workflow.mcp.reference.requiredMessage'),
              trigger: ['change', 'blur'],
            },
          ]"
        >
          <template #label>
            <div class="flex-between">
              <span class="mk-required">{{ t('workflow.mcp.serverConfig.label') }}</span>
              <el-select
                :teleported="false"
                v-model="form_data.mcp_source"
                :validate-event="false"
                size="small"
                class="w-23!"
                @change="changeMcpSource"
              >
                <el-option :label="`${t('common.options.reference')} MCP`" value="referencing" />
                <el-option :label="t('common.options.custom')" value="custom" />
              </el-select>
            </div>
          </template>
          <MdEditorMagnify
            v-if="form_data.mcp_source === 'custom'"
            :title="t('workflow.mcp.serverConfig.label')"
            v-model="form_data.mcp_servers"
            :placeholder="mcpServerJson"
            @wheel="handleNodeWheel"
          />
          <el-select v-else :teleported="false" v-model="form_data.mcp_tool_id" filterable @change="mcpToolSelectChange" @wheel="handleNodeWheel">
            <template v-for="mcpTool in mcpToolSelectOptions" :key="mcpTool.id">
              <el-option :label="mcpTool.name" :value="mcpTool.id">
                <div class="flex-align-center gap-2">
                  <ToolIcon :size="20" :icon="mcpTool.icon" :type="mcpTool.tool_type" />
                  <span>{{ mcpTool.name }}</span>
                  <el-tag v-if="mcpTool.scope === 'SHARED'" size="small" type="info">{{ t('resource.shared') }}</el-tag>
                </div>
              </el-option>
            </template>
          </el-select>
        </el-form-item>

        <!-- 工具 -->
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <span>{{ t('tool.title') }}</span>
              <!-- 获取 MCP 工具 -->
              <el-button type="primary" text @click="getTools">
                <MkIcon name="icon_refresh_outlined" />
              </el-button>
            </div>
          </template>
          <el-select v-model="form_data.mcp_tool" filterable :teleported="false" @change="changeTool" @wheel="handleNodeWheel">
            <el-option v-for="item in form_data.mcp_tools" :key="item.name" :label="item.name" :value="item.name">
              <div class="flex-align-center gap-1">
                <MkTooltip :content="item.description" placement="top-start">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </MkTooltip>
                <span>{{ item.name }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
    </div>
    <!-- 工具参数 -->
    <h6 class="mk-title-decoration mb-2 mt-2">{{ t('workflow.mcp.parameters.label') }}</h6>
    <div class="mk-gray-card">
      <el-form
        v-if="form_data.mcp_tool"
        ref="dynamicsFormRef"
        label-position="top"
        v-loading="loading"
        require-asterisk-position="right"
        :hide-required-asterisk="true"
        @submit.prevent
      >
        <el-form-item class="mk-hide-asterisk" v-for="item in form_data.tool_form_field" :key="item.field" :required="item.required">
          <template #label>
            <div class="flex-between">
              <TooltipLabel v-if="item.label.attrs?.tooltip" :label="item.label" :required="item.required" />
              <span v-else :class="item.required ? 'mk-required' : ''">{{ item.label.label }}</span>

              <el-select :teleported="false" v-model="item.source" size="small" class="w-21!" @change="setParamValue(item, '')">
                <el-option :label="t('common.options.referenceVariable')" value="referencing" />
                <el-option :label="t('common.options.custom')" value="custom" />
              </el-select>
            </div>
          </template>
          <el-input
            v-if="item.source === 'custom' && item.input_type === 'TextInput'"
            :model-value="paramsOf()[item.label.label]"
            @update:model-value="setParamValue(item, $event)"
            :placeholder="t('common.placeholders.input')"
          />
          <el-input-number
            v-else-if="item.source === 'custom' && item.input_type === 'NumberInput'"
            :model-value="paramsOf()[item.label.label]"
            @update:model-value="setParamValue(item, $event)"
            :placeholder="t('common.placeholders.input')"
          />
          <el-switch
            v-else-if="item.source === 'custom' && item.input_type === 'SwitchInput'"
            :model-value="paramsOf()[item.label.label]"
            @update:model-value="setParamValue(item, $event)"
            :placeholder="t('common.placeholders.input')"
          />
          <el-input
            v-else-if="item.source === 'custom' && item.input_type === 'JsonInput'"
            :model-value="paramsOf()[item.label.label]"
            @update:model-value="setParamValue(item, $event)"
            type="textarea"
            :placeholder="t('common.placeholders.input')"
          />
          <NodeCascader
            v-if="item.source === 'referencing'"
            :node-model="model"
            class="w-full"
            :placeholder="t('workflow.variable.selectPlaceholder')"
            :model-value="getParamReference(item)"
            @update:model-value="setParamValue(item, $event)"
          />
        </el-form-item>
      </el-form>
      <el-text v-else type="info">{{ t('common.empty.default') }}</el-text>
    </div>
    <McpServerInputDialog ref="mcpServerInputDialogRef" @refresh="handleMcpVariables" />
  </NodeContainer>
</template>
<style lang="scss" scoped></style>
