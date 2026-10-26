import { TOOL_TYPE } from '@/api/enums'
import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { AgentTool, JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'
import { useWorkflowStore, type McpTool } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'

/**
 * mcp-node（MCP 调用）的 AI 生成配置：引用资源库中的 MCP，选其中一个工具并为参数赋值。
 * node_data 协议以节点视图 index.vue 为准；自定义 MCP Server 配置需要用户提供，暂不由 AI 配置。
 */

interface SchemaProperty {
  description?: string
  type?: string
  properties?: Record<string, SchemaProperty>
  required?: string[]
}

const params: JsonObjectSchema = {
  type: 'object',
  properties: {},
  additionalProperties: { type: 'any', description: '引用上游的 MCP 工具参数，键为参数名（get_mcp_tools 返回的 params）' },
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    mcp_tool_id: { type: 'string', description: '资源库中的 MCP id（get_mcp_list 返回）' },
    mcp_tool: { type: 'string', description: '要调用的 MCP 工具名（get_mcp_tools 返回）' },
    values: { type: 'object', description: '常量参数：参数名 → 值；引用上游的参数由同名入参绑定' },
    is_result: { type: 'boolean', description: '是否把结果输出给用户，默认 false' },
  },
  required: ['mcp_tool_id', 'mcp_tool'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    result: { type: 'any', description: 'MCP 工具的返回结果' },
  },
  additionalProperties: false,
}

/** MCP 工具查询按画布所属资源（应用 / 工具 / 知识库）发起 */
function resourceTypeOf(mode: WorkflowMode) {
  if (mode === WorkflowMode.Tool || mode === WorkflowMode.ToolLoop) return 'tool'
  if (mode === WorkflowMode.Knowledge || mode === WorkflowMode.KnowledgeLoop) return 'knowledge'
  return 'application'
}

/** 与节点视图 changeTool 一致：参数可能整体嵌套在一个对象属性下 */
function paramFieldsOf(tool: McpTool) {
  const schema = tool.args_schema as { properties?: Record<string, SchemaProperty>; required?: string[] }
  const nestedEntry = Object.entries(schema.properties ?? {}).find(([, property]) => property.properties)
  const properties = nestedEntry ? (nestedEntry[1].properties ?? {}) : (schema.properties ?? {})
  const required = (nestedEntry ? nestedEntry[1].required : schema.required) ?? []
  return {
    nested: nestedEntry?.[0] ?? '',
    fields: Object.entries(properties).map(([name, property]) => ({
      name,
      type: property.type ?? 'string',
      description: property.description ?? '',
      required: required.includes(name),
    })),
  }
}

function inputTypeOf(type: string) {
  if (type === 'number' || type === 'integer') return 'NumberInput'
  if (type === 'boolean') return 'SwitchInput'
  if (type === 'array' || type === 'object') return 'JsonInput'
  return 'TextInput'
}

function useAgent(context: NodeAgentContext) {
  const store = useWorkflowStore(context.bindings.resourceScope)

  /** 连接所选 MCP 拉取工具列表；Server 配置含 {{变量}} 时需要用户填写，AI 不处理 */
  async function loadMcpTools(mcpToolId: string): Promise<{ servers: string; tools: McpTool[] } | string> {
    const resourceId = context.bindings.resourceId
    if (!resourceId) return '缺少画布所属资源 id，无法查询 MCP 工具'
    const mcp = await store.getToolById(mcpToolId).catch(() => null)
    const servers = typeof mcp?.code === 'string' ? mcp.code : ''
    if (!servers) return `MCP 不存在或缺少 Server 配置：${mcpToolId}`
    if (/\{\{\s*[A-Za-z_][\w.]*\s*\}\}/.test(servers)) return '该 MCP 的 Server 配置含需要用户填写的变量，请改用其他 MCP 或让用户手动配置'
    const tools = await store.getMcpTools(resourceTypeOf(context.workflowMode), resourceId, servers).catch(() => null)
    if (!tools) return '获取 MCP 工具失败，请检查 MCP Server 配置'
    return { servers, tools }
  }

  const mcpListTool: AgentTool = {
    name: 'get_mcp_list',
    description: '列出资源库中可用的 MCP [{id,name,desc}]。',
    parameters: { type: 'object', properties: {} },
    apply: async () =>
      (await store.getToolListWithShared({ tool_type: TOOL_TYPE.MCP }))
        .filter((tool) => tool.is_active && tool.tool_type === TOOL_TYPE.MCP)
        .map(({ id, name, desc }) => ({ id, name, desc })),
  }

  const mcpToolsTool: AgentTool = {
    name: 'get_mcp_tools',
    description: '连接某个 MCP 并列出其工具 [{name, description, params:[{name,type,description,required}]}]。',
    parameters: { type: 'object', properties: { mcp_tool_id: { type: 'string' } }, required: ['mcp_tool_id'] },
    apply: async (args) => {
      const loaded = await loadMcpTools(String(args.mcp_tool_id))
      if (typeof loaded === 'string') return { error: loaded }
      return loaded.tools.map((tool) => ({ name: tool.name, description: tool.description, params: paramFieldsOf(tool).fields }))
    },
  }

  return useNodeAgent(context, {
    prompt: [
      'mcp-node（MCP 调用）配置要点：',
      '- 先 get_mcp_list 选 MCP，再 get_mcp_tools 看它的工具与参数，按需求选一个工具。',
      '- 引用上游数据的参数由同名入参绑定；其余参数在 values 里给常量值，必填参数都要有值。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前 MCP 调用节点：选择要调用的 MCP 工具并为参数赋值。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const mcpToolId = String(args.mcp_tool_id ?? '')
          const loaded = await loadMcpTools(mcpToolId)
          if (typeof loaded === 'string') return new ErrorResult(loaded)
          const tool = loaded.tools.find((item) => item.name === args.mcp_tool)
          if (!tool) return new ErrorResult(`MCP 工具不存在：${String(args.mcp_tool)}，可选：${loaded.tools.map((item) => item.name).join('、')}`)
          const { nested, fields } = paramFieldsOf(tool)
          const values = (args.values ?? {}) as Record<string, unknown>
          const toolParams: Record<string, unknown> = {}
          const toolFormField = []
          for (const field of fields) {
            const reference = argReference(context, field.name)
            const value = reference ? [...reference] : values[field.name]
            if (value === undefined && field.required) {
              return new ErrorResult(`必填参数 ${field.name} 未赋值（引用上游请让父节点传入同名入参，常量写在 values）`)
            }
            if (value !== undefined) toolParams[field.name] = value
            toolFormField.push({
              field: field.name,
              label: { input_type: 'TooltipLabel', label: field.name, attrs: { tooltip: field.description } },
              input_type: inputTypeOf(field.type),
              source: reference ? 'referencing' : 'custom',
              required: field.required,
            })
          }
          const nodeData = readNodeData<Record<string, unknown>>(node)
          writeNodeProperties(node, {
            node_data: {
              ...nodeData,
              mcp_source: 'referencing',
              mcp_tool_id: mcpToolId,
              mcp_servers: loaded.servers,
              mcp_tools: loaded.tools,
              mcp_tool: tool.name,
              mcp_server: tool.server,
              params_nested: nested,
              tool_form_field: toolFormField,
              tool_params: nested ? { [nested]: toolParams } : toolParams,
              is_result: typeof args.is_result === 'boolean' ? args.is_result : (nodeData.is_result ?? false),
            },
          })
          return finishWithValidate(context)
        },
      },
      mcpListTool,
      mcpToolsTool,
    ],
  })
}

export default {
  description: '调用资源库中某个 MCP 服务的工具（搜索、查询外部系统等），入参为该工具中引用上游数据的参数',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
