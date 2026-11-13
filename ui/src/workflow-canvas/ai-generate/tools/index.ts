import { cloneDeep } from 'lodash'
import { TOOL_TYPE } from '@/api/enums'
import type { ToolItem } from '@/api/types'
import type LogicFlow from '@logicflow/core'
import type { BaseNodeModel } from '@logicflow/core'
import { WorkFlowInstance, KnowledgeWorkFlowInstance, ToolWorkFlowInstance } from '@/workflow-canvas/core/validate'
import { toolLibNode } from '@/workflow-canvas/config/node-data'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowKind, WorkflowMode, WorkflowNodeType, type ShapeItem } from '@/workflow-canvas/types'
import {
  fixedNodeTypesOf,
  MAIN_LF_ID,
  VARIABLE_GROUPS,
  addEdge,
  addNode,
  findNodeCanvas,
  findNodeTemplate,
  getNode,
  getOutgoingAnchors,
  layoutCanvas,
  listCanvases,
  nodeNameOf,
  nodeOutputFields,
  readNodeData,
  resolveCanvas,
  resolveSourceAnchor,
  validateReference,
  writeNodeProperties,
  type CanvasRef,
} from './canvas'
import { createAgent } from '../create-agent'
import { formatValidationError, isReference, isStructuredSchema, schemaType } from './node'
import { ErrorResult } from './result'
import type { AgentBindings, AgentTool, JsonSchema, NodeAgentModule, NodeReference } from '../type'


/** 节点配置 agent 取自各节点 index.ts 默认导出的 agent 字段；未提供的节点可新增、连线，但不能 AI 配置 */
const nodeRegistryModules = import.meta.glob<{ default: { type: string; agent?: NodeAgentModule } }>('../../nodes/*/index.ts', { eager: true })
const nodeAgentByType = new Map(
  Object.values(nodeRegistryModules).flatMap(({ default: node }) => (node.agent ? [[node.type, node.agent] as const] : [])),
)

export function nodeAgentFor(type: string): NodeAgentModule | undefined {
  return nodeAgentByType.get(type)
}

/**
 * 建图工具（各画布父 agent 共用）：查看画布、取出口、加删节点与连线、委派节点配置、校验。
 * 都带 lf_id 跨画布操作：主画布 "main"（或省略），循环体为所属循环节点 id。
 */

const LF_ID_SCHEMA = { type: 'string', description: '画布：主画布 "main"（或省略）；循环体传所属循环节点 id' }
const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

/** 提示词等文本里的变量 {{节点名称.字段}} */
const PROMPT_VARIABLE_PATTERN = /\{\{[^{}]+?\.[^{}]+?\}\}/g

/**
 * 节点的数据引用：扫描 node_data 里所有 [节点ID, 字段]（首项须为画布上的节点或变量分组，避免把普通二元数组误判），
 * x-bind 写入的字段标出对应形参名；文本里的 {{节点名称.字段}} 单独列出。
 */
function referencesOf(node: BaseNodeModel, knownSources: Set<string>) {
  const params = nodeAgentFor(String(node.type))?.params.properties ?? {}
  const paramByField = new Map(Object.entries(params).flatMap(([name, schema]) => (typeof schema['x-bind'] === 'string' ? [[schema['x-bind'], name] as const] : [])))
  const references: Array<{ param?: string; field: string; ref: NodeReference }> = []
  const variables = new Set<string>()
  const visit = (value: unknown, path: string, topField: string) => {
    if (typeof value === 'string') {
      value.match(PROMPT_VARIABLE_PATTERN)?.forEach((variable) => variables.add(variable))
    } else if (isReference(value) && knownSources.has(value[0])) {
      const param = paramByField.get(topField)
      references.push({ ...(param ? { param } : {}), field: path, ref: [...value] })
    } else if (Array.isArray(value)) {
      value.forEach((item, index) => visit(item, `${path}[${index}]`, topField))
    } else if (value && typeof value === 'object') {
      Object.entries(value).forEach(([key, item]) => visit(item, path ? `${path}.${key}` : key, topField || key))
    }
  }
  visit(node.properties.node_data ?? {}, '', '')
  return { references, prompt_variables: [...variables] }
}

/** 画布骨架：节点（id / 类型 / 名称 / 输出字段 / 数据引用）与连线，不含配置内容（配置用 get_node_detail 取） */
function describeCanvas(canvas: CanvasRef, knownSources: Set<string>) {
  const nodes = canvas.lf.graphModel.nodes.filter((node) => String(node.type) !== WorkflowNodeType.LoopBodyNode)
  return {
    lf_id: canvas.lfId,
    nodes: nodes.map((node) => {
      const { references, prompt_variables } = referencesOf(node, knownSources)
      return {
        id: node.id,
        type: String(node.type),
        name: nodeNameOf(node),
        outputs: nodeOutputFields(node).map((field) => field.value),
        ...(references.length ? { references } : {}),
        ...(prompt_variables.length ? { prompt_variables } : {}),
      }
    }),
    edges: canvas.lf.graphModel.edges
      .filter((edge) => edge.type !== 'loop-edge')
      .map((edge) => {
        const source = canvas.lf.graphModel.getNodeModelById(edge.sourceNodeId)
        const label = source ? getOutgoingAnchors(source).find((anchor) => anchor.anchorId === edge.sourceAnchorId)?.label : undefined
        return { source_anchor_id: edge.sourceAnchorId, from: edge.sourceNodeId, outlet: label, to: edge.targetNodeId }
      }),
  }
}

/** 可被引用的来源：全部画布上的节点 id 与变量分组 */
function knownSourcesOf(canvases: CanvasRef[]): Set<string> {
  return new Set([...VARIABLE_GROUPS, ...canvases.flatMap((canvas) => canvas.lf.graphModel.nodes.map((node) => node.id))])
}

async function canvasOrError(bindings: AgentBindings, lfId: unknown) {
  return resolveCanvas(bindings.rootLf, bindings.workflowMode, typeof lfId === 'string' ? lfId : undefined)
}

export function getCanvasDetailTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'get_canvas_detail',
    description:
      '查看整张工作流的骨架：主画布与各循环体（loopBodies[循环节点id]）的节点（id / type / name / 输出字段 outputs）、连线 edges，' +
      '以及每个节点的数据引用 references（param 形参名、field 写入的配置字段、ref 引用的 [节点ID, 字段]）和文本里用到的变量 prompt_variables。' +
      '不含节点配置内容（代码、提示词、阈值等），需要时用 get_node_detail 取。工具工作流另带 tool_params（基本信息声明的输入 / 输出参数）。',
    parameters: { type: 'object', properties: {} },
    resultLimit: 20000,
    apply: async () => {
      const canvases = await listCanvases(bindings.rootLf, bindings.workflowMode)
      const knownSources = knownSourcesOf(canvases)
      const [main, ...loops] = canvases
      return {
        ...(isToolMode(bindings.workflowMode) ? { tool_params: toolParamsOf(bindings.rootLf) } : {}),
        main: describeCanvas(main!, knownSources),
        loopBodies: Object.fromEntries(loops.map((canvas) => [canvas.lfId, describeCanvas(canvas, knownSources)])),
      }
    },
  }
}

export function getNodeDetailTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'get_node_detail',
    description:
      '查看指定节点的完整配置，可一次传多个节点 id：完整 node_data（代码、提示词、引用字段等，不截断）、输出字段、数据引用与上下游节点。' +
      '修改已有节点或排查问题前，先用它看清相关节点的现状；倒查一条链路时把链上节点一次传入。',
    parameters: {
      type: 'object',
      properties: { nodeIds: { type: 'array', items: { type: 'string' }, description: '节点 id 列表（任意画布，含循环体内节点）' } },
      required: ['nodeIds'],
    },
    resultLimit: 30000,
    apply: async (args) => {
      const nodeIds = (Array.isArray(args.nodeIds) ? args.nodeIds : [args.nodeIds ?? args.nodeId]).filter(Boolean).map(String)
      if (!nodeIds.length) return new ErrorResult('nodeIds 至少传一个节点 id')
      const knownSources = knownSourcesOf(await listCanvases(bindings.rootLf, bindings.workflowMode))
      const details = []
      for (const nodeId of nodeIds) {
        const canvas = await findNodeCanvas(bindings.rootLf, bindings.workflowMode, nodeId)
        const node = canvas ? getNode(canvas.lf, nodeId) : undefined
        if (!canvas || !node) {
          details.push({ id: nodeId, error: '节点不存在' })
          continue
        }
        const brief = (target: BaseNodeModel) => ({ id: target.id, type: String(target.type), name: nodeNameOf(target) })
        details.push({
          lf_id: canvas.lfId,
          ...brief(node),
          outputs: nodeOutputFields(node).map((field) => field.value),
          ...referencesOf(node, knownSources),
          upstream: canvas.lf.graphModel.getNodeIncomingNode(nodeId).map(brief),
          downstream: canvas.lf.graphModel.getNodeOutgoingNode(nodeId).map(brief),
          node_data: node.properties.node_data ?? {},
        })
      }
      return { nodes: details }
    },
  }
}

/** 运行值的摘要：标出真实类型（dict / list 及长度），内容截断，供核对上下游数据结构 */
function summarizeRunValue(value: unknown): unknown {
  if (value === null || value === undefined || typeof value === 'number' || typeof value === 'boolean') return value
  const kind = Array.isArray(value) ? `list(${value.length})` : typeof value === 'object' ? 'dict' : 'str'
  const text = typeof value === 'string' ? value : JSON.stringify(value)
  return `<${kind}> ${text.length > 400 ? `${text.slice(0, 400)}…` : text}`
}

const RUN_BASE_FIELDS = ['node_id', 'name', 'type', 'index', 'status', 'run_time', 'error', 'err_message']

export function getLastRunTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'get_last_run',
    description:
      '查看当前知识库工作流最近一次执行（调试或导入）的详情：整体状态，以及按执行顺序每个节点的状态、报错原文和实际输入输出（值前标注真实类型 <dict> / <list(n)> / <str>，内容截断）。' +
      '用户反馈运行报错或结果不对时先调它定位，再决定改哪个节点。执行的是当时保存的画布，之后改过的节点以画布现状为准。',
    parameters: { type: 'object', properties: {} },
    resultLimit: 20000,
    apply: async () => {
      if (!bindings.resourceId) return new ErrorResult('缺少知识库 id，无法查询执行记录')
      const action = await useWorkflowStore(bindings.resourceScope).getLatestKnowledgeAction(bindings.resourceId)
      if (!action) return { found: false, message: '没有执行记录：请用户先调试运行一次，或直接提供报错信息' }
      const nodes = Object.values(action.details ?? {})
        .sort((left, right) => Number(left.index ?? 0) - Number(right.index ?? 0))
        .map((detail) => ({
          node_id: detail.node_id,
          name: detail.name,
          type: detail.type,
          status: detail.status === 200 ? 'success' : detail.status === 500 ? 'error' : detail.status,
          error: detail.err_message || detail.error || undefined,
          data: Object.fromEntries(
            Object.entries(detail)
              .filter(([key, value]) => !RUN_BASE_FIELDS.includes(key) && value !== null && value !== undefined && value !== '')
              .map(([key, value]) => [key, summarizeRunValue(value)]),
          ),
        }))
      return { found: true, state: action.state, create_time: action.create_time, nodes }
    },
  }
}

// ============================================================
// 工具工作流的函数签名（基本信息节点的输入 / 输出参数）
// ============================================================

type ToolParamField = { field: string; label?: string; type?: string; desc?: string; is_required?: boolean; default_value?: unknown }

function isToolMode(mode: WorkflowMode): boolean {
  return mode === WorkflowMode.Tool || mode === WorkflowMode.ToolLoop
}

function toolParamFields(lf: LogicFlow, key: 'user_input_field_list' | 'user_output_field_list'): ToolParamField[] {
  const fields = getNode(lf, WorkflowNodeType.ToolBaseNode)?.properties[key]
  return Array.isArray(fields) ? (fields as ToolParamField[]) : []
}

/** 工具工作流的函数签名：输入参数（开始节点提供为 global）与输出参数（由变量赋值写入 output） */
function toolParamsOf(lf: LogicFlow) {
  return {
    inputs: toolParamFields(lf, 'user_input_field_list').map((field) => ({
      field: field.field,
      label: field.label,
      type: field.type,
      is_required: field.is_required,
      desc: field.desc,
      ref: ['global', field.field],
    })),
    outputs: toolParamFields(lf, 'user_output_field_list').map((field) => ({ field: field.field, label: field.label, ref: ['output', field.field] })),
  }
}

/** 引用了基本信息里不存在的输入 / 输出参数的位置（参数被改名或删除后会出现） */
function brokenToolParamReferences(lf: LogicFlow, canvases: CanvasRef[]): string[] {
  const declared: Record<string, Set<string>> = {
    global: new Set(toolParamFields(lf, 'user_input_field_list').map((field) => field.field)),
    output: new Set(toolParamFields(lf, 'user_output_field_list').map((field) => field.field)),
  }
  const knownSources = knownSourcesOf(canvases)
  return canvases.flatMap((canvas) =>
    canvas.lf.graphModel.nodes.flatMap((node) =>
      referencesOf(node, knownSources)
        .references.filter(({ ref }) => declared[ref[0]] && !declared[ref[0]]!.has(ref[1]))
        .map(({ ref, field }) => `节点「${nodeNameOf(node)}」(${node.id}) 的 ${field} 引用了未声明的${ref[0] === 'global' ? '输入' : '输出'}参数 ${ref[0]}.${ref[1]}`),
    ),
  )
}

/** 没有任何变量赋值节点写入、也没有默认值的输出参数：调用方拿不到这个字段 */
function unwrittenToolOutputs(lf: LogicFlow, canvases: CanvasRef[]): string[] {
  const written = new Set(
    canvases.flatMap((canvas) =>
      canvas.lf.graphModel.nodes
        .filter((node) => String(node.type) === WorkflowNodeType.VariableAssignNode)
        .flatMap((node) => (node.properties.node_data as { variable_list?: Array<{ fields?: string[] }> } | undefined)?.variable_list ?? [])
        .filter((variable) => variable.fields?.[0] === 'output')
        .map((variable) => String(variable.fields?.[1])),
    ),
  )
  return toolParamFields(lf, 'user_output_field_list')
    .filter((field) => !written.has(field.field) && (field.default_value === undefined || field.default_value === null))
    .map((field) => field.field)
}

export function getNodeAnchorsTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'get_node_anchors',
    description:
      '取节点的全部出口（判断器 / 意图识别每个分支一个出口），返回 [{source_anchor_id, label, connected_to}]，连接分支下游时传其 source_anchor_id。',
    parameters: { type: 'object', properties: { nodeId: { type: 'string' }, lf_id: LF_ID_SCHEMA }, required: ['nodeId'] },
    apply: async (args) => {
      const canvas = await canvasOrError(bindings, args.lf_id)
      if ('error' in canvas) return canvas
      const node = getNode(canvas.lf, String(args.nodeId))
      if (!node) return { error: `节点不存在: ${args.nodeId}` }
      return getOutgoingAnchors(node).map((anchor) => ({
        source_anchor_id: anchor.anchorId,
        label: anchor.label,
        connected_to: canvas.lf.graphModel.edges.filter((edge) => edge.sourceAnchorId === anchor.anchorId).map((edge) => edge.targetNodeId),
      }))
    },
  }
}

/** 工具节点的模板：按工具详情补齐参数与名称，与资源菜单拖入的节点一致；数据源工具额外写入 kind / condition */
async function toolNodeTemplate(bindings: AgentBindings, toolId: string): Promise<ShapeItem | { error: string }> {
  const tool = await useWorkflowStore(bindings.resourceScope)
    .force.getToolById(toolId)
    .catch(() => null)
  if (!tool?.id) return { error: `工具不存在: ${toolId}` }
  const inputFields = (tool.input_field_list ?? []).map((field) => ({ ...field, value: field.source === 'reference' ? [] : '' }))
  const dataSource = tool.tool_type === TOOL_TYPE.DATA_SOURCE ? { kind: WorkflowKind.DataSource, condition: 'OR' } : {}
  return {
    ...cloneDeep(toolLibNode),
    properties: {
      ...cloneDeep(toolLibNode.properties),
      stepName: tool.name,
      ...dataSource,
      node_data: { ...cloneDeep(tool), input_field_list: inputFields, tool_lib_id: tool.id },
    },
  }
}

/** 工具列表 → 精简结构，供 get_tools / list_datasource 复用 */
function summarizeTools(tools: ToolItem[]) {
  return tools.map((tool) => ({
    id: tool.id,
    name: tool.name,
    desc: tool.desc,
    inputs: (tool.input_field_list ?? []).map((field) => ({
      name: field.name,
      type: field.type,
      source: field.source,
      is_required: field.is_required,
      desc: field.desc,
    })),
  }))
}

/** 列出可在应用工作流中使用的自定义工具（父 agent 选型用） */
export function getToolsTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'get_tools',
    description: '列出可用的自定义工具 [{id,name,desc,inputs:[{name,type,source,is_required,desc}]}]，add_node 新增 tool-lib-node 时传其 tool_id。',
    parameters: { type: 'object', properties: {} },
    apply: async () => {
      const tools = await useWorkflowStore(bindings.resourceScope).getToolListWithShared({ tool_type: TOOL_TYPE.CUSTOM })
      return summarizeTools(tools.filter((tool) => tool.is_active && tool.tool_type === TOOL_TYPE.CUSTOM))
    },
  }
}

/** 列出知识库工作流可用的数据源（Data source 工具）；作为知识库工作流的入口节点 */
export function listDataSourceTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'list_datasource',
    description:
      '列出可用的数据源 [{id,name,desc,inputs:[...]}]。知识库工作流的入口是数据源节点，用 add_node(type="tool-lib-node", tool_id) 新建（无需 source_anchor_id）。',
    parameters: { type: 'object', properties: {} },
    apply: async () => {
      const tools = await useWorkflowStore(bindings.resourceScope).getToolListWithShared({ tool_type: TOOL_TYPE.DATA_SOURCE })
      return summarizeTools(tools.filter((tool) => tool.is_active && tool.tool_type === TOOL_TYPE.DATA_SOURCE))
    },
  }
}

export function addNodeTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'add_node',
    description:
      '新增节点并从上游出口接一条入边（建即接，杜绝孤立节点）；可新增的节点与当前画布的节点菜单一致。' +
      'source_anchor_id：普通连接传上游节点 id；接判断器/意图识别某分支时传 get_node_anchors 返回的出口 id；循环体首个节点接 "loop-start-node"。' +
      'tool-lib-node 需同时传 tool_id（get_tools 或 list_datasource 查询）。' +
      '数据源节点（本地文件 / Web 站点 / 数据源工具）是流程入口，不接上游，必须省略 source_anchor_id。' +
      '返回 { nodeId, name, outputs }；带 note 表示该节点暂不支持 AI 配置。',
    parameters: {
      type: 'object',
      properties: {
        type: { type: 'string', description: '节点类型（节点目录中的 type）' },
        source_anchor_id: { type: 'string', description: '上游节点 id 或出口 id；仅数据源节点省略' },
        name: { type: 'string', description: '节点名称（可选，体现用途，如 "产品知识检索"）' },
        tool_id: { type: 'string', description: 'type=tool-lib-node 时必填' },
        lf_id: LF_ID_SCHEMA,
      },
      required: ['type'],
    },
    apply: async (args) => {
      const canvas = await canvasOrError(bindings, args.lf_id)
      if ('error' in canvas) return canvas
      const type = String(args.type)
      if (fixedNodeTypesOf(canvas.mode).includes(type)) return new ErrorResult(`${type} 是画布固定节点，已存在且只能有一个，不能新增${nodeAgentFor(type) ? '；要修改它用 configure_node' : ''}`)
      let template: ShapeItem | { error: string } | undefined
      if (type === WorkflowNodeType.ToolLib) {
        if (!args.tool_id) return { error: 'tool-lib-node 需要 tool_id，先 get_tools / list_datasource 查询' }
        template = await toolNodeTemplate(bindings, String(args.tool_id))
      } else {
        template = findNodeTemplate(canvas.mode, type)
      }
      if (!template) {
        const where = canvas.lfId === MAIN_LF_ID ? '主画布' : '循环体内'
        return { error: `${where}不能使用 ${type}：不在该画布的节点菜单中，请从节点目录中选择（Break/Continue 只能建在循环体内）` }
      }
      if ('error' in template) return template
      const override = args.name ? { stepName: String(args.name) } : {}
      const created = (node: ReturnType<typeof addNode>) => ({
        nodeId: node.id,
        name: nodeNameOf(node),
        lf_id: canvas.lfId,
        outputs: nodeOutputFields(node),
        ...(nodeAgentFor(type) ? {} : { note: '该节点暂不支持 AI 配置：不要对它 configure_node，完成后提示用户手动配置' }),
      })
      // 数据源节点是流程入口，没有入口锚点：不接上游；其余节点必须建即接
      const sourceAnchor = typeof args.source_anchor_id === 'string' ? args.source_anchor_id.trim() : ''
      if (template.properties?.kind === WorkflowKind.DataSource) {
        if (sourceAnchor) return { error: '数据源节点是流程入口，不能接上游，请省略 source_anchor_id' }
        return created(addNode(canvas.lf, template, '', override))
      }
      if (!sourceAnchor) return { error: 'source_anchor_id 必填：只有数据源节点可以不接上游' }
      const source = resolveSourceAnchor(canvas.lf, sourceAnchor)
      if ('error' in source) return source
      const node = addNode(canvas.lf, template, source.node.id, override)
      const error = addEdge(canvas.lf, source.node.id, source.anchorId, node.id)
      if (error) return { error }
      return created(node)
    },
  }
}

export function addEdgeTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'add_edge',
    description: '在同一画布内补一条连线（如多分支汇合到同一节点）。source_anchor_id 为上游节点 id 或出口 id，target 为下游节点 id。',
    parameters: {
      type: 'object',
      properties: { source_anchor_id: { type: 'string' }, target: { type: 'string' }, lf_id: LF_ID_SCHEMA },
      required: ['source_anchor_id', 'target'],
    },
    apply: async (args) => {
      const canvas = await canvasOrError(bindings, args.lf_id)
      if ('error' in canvas) return canvas
      const source = resolveSourceAnchor(canvas.lf, String(args.source_anchor_id))
      if ('error' in source) return source
      const target = getNode(canvas.lf, String(args.target))
      if (!target) return { error: `目标节点不在该画布: ${args.target}` }
      if (fixedNodeTypesOf(canvas.mode).includes(String(target.type))) return { error: '固定节点不能作为连线终点' }
      if (target.properties.kind === WorkflowKind.DataSource) return { error: '数据源节点是流程入口，不能作为连线终点' }
      const error = addEdge(canvas.lf, source.node.id, source.anchorId, target.id)
      return error ? { error } : { ok: true }
    },
  }
}

export function deleteNodeTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'delete_node',
    description: '删除节点及其连线（固定节点不可删除；删除循环节点会一并删除其循环体）。',
    parameters: { type: 'object', properties: { nodeId: { type: 'string' }, lf_id: LF_ID_SCHEMA }, required: ['nodeId'] },
    apply: async (args) => {
      const canvas = await canvasOrError(bindings, args.lf_id)
      if ('error' in canvas) return canvas
      const node = getNode(canvas.lf, String(args.nodeId))
      if (!node) return { error: `节点不存在: ${args.nodeId}` }
      if (fixedNodeTypesOf(canvas.mode).includes(String(node.type))) {
        return new ErrorResult(`${node.type} 是画布固定节点，不能删除${nodeAgentFor(String(node.type)) ? '；要修改它用 configure_node' : ''}`)
      }
      const downstream = canvas.lf.graphModel.getNodeOutgoingNode(node.id)
      canvas.lf.graphModel
        .getNodeOutgoingNode(node.id)
        .filter((item) => String(item.type) === WorkflowNodeType.LoopBodyNode)
        .forEach((body) => canvas.lf.deleteNode(body.id))
      canvas.lf.deleteNode(node.id)
      downstream.forEach((item) => (item as unknown as { clearNextNodeField?: (containSelf: boolean) => void }).clearNextNodeField?.(true))
      return { ok: true }
    },
  }
}

export function deleteEdgeTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'delete_edge',
    description: '删除一条连线：source_anchor_id 为出口 id（或上游节点 id），target 为下游节点 id。',
    parameters: {
      type: 'object',
      properties: { source_anchor_id: { type: 'string' }, target: { type: 'string' }, lf_id: LF_ID_SCHEMA },
      required: ['source_anchor_id', 'target'],
    },
    apply: async (args) => {
      const canvas = await canvasOrError(bindings, args.lf_id)
      if ('error' in canvas) return canvas
      const sourceAnchorId = String(args.source_anchor_id)
      const edges = canvas.lf.graphModel.edges.filter(
        (edge) => edge.targetNodeId === args.target && (edge.sourceAnchorId === sourceAnchorId || edge.sourceNodeId === sourceAnchorId),
      )
      if (!edges.length) return { error: '连线不存在' }
      edges.forEach((edge) => canvas.lf.deleteEdge(edge.id))
      getNode(canvas.lf, String(args.target))?.clearNextNodeField(true)
      return { ok: true }
    },
  }
}

// ============================================================
// 节点配置委派
// ============================================================

/** 上游引用的返回类型：取上游节点函数 returns 声明的固定字段类型，未声明（动态字段、开始节点、全局变量）返回 undefined */
function referenceType(lf: LogicFlow, [refNodeId, field]: NodeReference): string | undefined {
  const refNode = getNode(lf, refNodeId)
  const returns = refNode ? nodeAgentFor(String(refNode.type))?.returns : undefined
  const type = returns?.properties[field]?.type
  return typeof type === 'string' ? type : undefined
}

/** 按形参 schema 校验实参：形参存在、引用合法、array / object 形参的上游类型对得上 */
function checkArgs(
  lf: LogicFlow,
  nodeId: string,
  module: NodeAgentModule,
  rawArgs: unknown,
): { args: Record<string, NodeReference | NodeReference[]> } | { error: string } {
  const input = rawArgs && typeof rawArgs === 'object' ? (rawArgs as Record<string, unknown>) : {}
  const { properties, required = [], additionalProperties } = module.params
  const missing = required.filter((name) => input[name] === undefined)
  if (missing.length) return { error: `缺少入参：${missing.join('、')}` }
  const args: Record<string, NodeReference | NodeReference[]> = {}
  for (const [name, value] of Object.entries(input)) {
    const schema = (properties[name] ?? (typeof additionalProperties === 'object' ? additionalProperties : undefined)) as JsonSchema | undefined
    if (!schema) return { error: `没有入参 ${name}，可用入参：${Object.keys(properties).join('、') || '无'}` }
    // 带 items 的 array 形参可接收多个引用（如提示词素材、重排内容），其余形参只接收一个引用；
    // x-single 表示 items 只描述引用值的元素结构，仍只接一个引用（如知识库写入的文档列表）
    const multiple = schema.type === 'array' && schema.items !== undefined && schema['x-single'] !== true
    const references = isReference(value) ? [value] : multiple && Array.isArray(value) && value.every(isReference) ? (value as NodeReference[]) : undefined
    if (!references) return { error: multiple ? `入参 ${name} 应为引用 [节点ID, 字段] 或其列表` : `入参 ${name} 应为一个引用 [节点ID, 字段]` }
    // 多引用形参逐个按 items 类型比对，单引用形参按形参类型比对
    const expectedType = multiple ? (schema.items as JsonSchema).type : schema.type
    for (const reference of references) {
      const error = validateReference(lf, nodeId, reference, `入参 ${name}`)
      if (error) return { error }
      const actualType = referenceType(lf, reference)
      if ((expectedType === 'array' || expectedType === 'object') && actualType && actualType !== expectedType && actualType !== 'any') {
        return { error: `入参 ${name} 需要 ${expectedType}，引用的 ${reference.join('.')} 为 ${actualType}` }
      }
    }
    args[name] = multiple ? references : references[0]!
  }
  return { args }
}

/** 已绑定引用的值结构：上游 returns 对该字段逐字段声明了结构时渲染出来，供配置 agent 按真实结构处理数据 */
function argStructuresOf(lf: LogicFlow, args: Record<string, NodeReference | NodeReference[]>): Record<string, string> {
  const structures: Record<string, string> = {}
  for (const value of Object.values(args)) {
    for (const [refNodeId, field] of isReference(value) ? [value] : value) {
      const refNode = getNode(lf, refNodeId)
      const schema = refNode ? nodeAgentFor(String(refNode.type))?.returns.properties[field] : undefined
      if (isStructuredSchema(schema)) structures[`${refNodeId}.${field}`] = schemaType(schema)
    }
  }
  return structures
}

/**
 * 直连下游节点需要的结构化入参：本节点的输出通常就是它们的实参（如自定义代码 → 知识库写入的 documents），
 * 配置时把目标结构告诉本节点，让产出服务于下游，而不是等下游绑定时才发现结构不符。
 */
function downstreamContractsOf(lf: LogicFlow, nodeId: string): string[] {
  return lf.graphModel.getNodeOutgoingNode(nodeId).flatMap((target) => {
    const module = nodeAgentFor(String(target.type))
    if (!module) return []
    const name = nodeNameOf(target)
    return Object.entries(module.params.properties)
      .filter(([, schema]) => isStructuredSchema(schema))
      .map(([param, schema]) => {
        const description = typeof schema.description === 'string' ? `（${schema.description}）` : ''
        return `- ${name}（${target.type}）的入参 ${param}${description}：${schemaType(schema)}`
      })
  })
}

/** x-bind 形参：实参由框架直接写入 node_data 的对应字段 */
function writeBoundArgs(node: ReturnType<typeof getNode>, module: NodeAgentModule, args: Record<string, NodeReference | NodeReference[]>) {
  if (!node) return
  const boundData: Record<string, unknown> = {}
  for (const [name, value] of Object.entries(args)) {
    const field = module.params.properties[name]?.['x-bind']
    if (typeof field !== 'string') continue
    boundData[field] = isReference(value) ? [...value] : value.map((reference) => [...reference])
  }
  if (Object.keys(boundData).length) writeNodeProperties(node, { node_data: { ...readNodeData<Record<string, unknown>>(node), ...boundData } })
}

export function configureNodeTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'configure_node',
    description:
      '把节点当函数调用：args 传实参（形参名 → 上游引用 [节点ID, 字段]，可多个时传列表），由框架校验并绑定；' +
      'requirement 写配置要求（按节点目录里该节点的配置项描述：提示词等生成内容只写要生成什么，模型、知识库等资源只写意图，别猜 id）；' +
      '节点有按配置生成的返回字段时，returns 列出要求产出的字段名，下游按这些字段引用。' +
      '多个节点可在同一轮并发配置。返回 { nodeId, result:{ outputs } } 或 { nodeId, error }。',
    parameters: {
      type: 'object',
      properties: {
        nodeId: { type: 'string' },
        args: { type: 'object', description: '实参：形参名 → [节点ID, 字段] 或其列表' },
        requirement: { type: 'string', description: '配置要求' },
        returns: { type: 'array', items: { type: 'string' }, description: '要求产出的动态返回字段名（可选）' },
        lf_id: LF_ID_SCHEMA,
      },
      required: ['nodeId', 'requirement'],
    },
    apply: (args) => {
      let child: ReturnType<typeof createAgent> | undefined
      const promise = (async () => {
        const nodeId = String(args.nodeId)
        const canvas = await findNodeCanvas(bindings.rootLf, bindings.workflowMode, nodeId)
        if (!canvas) return new ErrorResult(`节点不存在: ${nodeId}`, { nodeId })
        const node = getNode(canvas.lf, nodeId)!
        const module = nodeAgentFor(String(node.type))
        if (!module) return new ErrorResult(`${node.type} 暂不支持 AI 配置，请在总结里提示用户手动配置`, { nodeId })
        const checked = checkArgs(canvas.lf, nodeId, module, args.args)
        if ('error' in checked) return new ErrorResult(checked.error, { nodeId })
        // 等待节点表单完成挂载与默认值初始化，再写入配置
        await sleep(80)
        writeBoundArgs(getNode(canvas.lf, nodeId), module, checked.args)
        const childBindings: AgentBindings = {
          ...bindings,
          position: [...(bindings.position ?? []), nodeId],
          messages: undefined,
          maxIterations: 30,
        }
        const requirement = typeof args.requirement === 'string' ? args.requirement.trim() : ''
        const expectedReturns = Array.isArray(args.returns) ? args.returns.map(String) : []
        child = createAgent(
          module.useAgent({
            lf: canvas.lf,
            nodeId,
            workflowMode: canvas.mode,
            bindings: childBindings,
            args: checked.args,
            requirement,
            expectedReturns,
            argStructures: argStructuresOf(canvas.lf, checked.args),
            downstream: downstreamContractsOf(canvas.lf, nodeId),
          }),
        )
        const result = await child.run(
          requirement ? `请按以下要求配置本节点（生成内容的字段按描述生成完整内容，资源字段查出真实 id）：\n${requirement}` : '请结合整体目标与已绑定入参，自行判断并配置本节点。',
        )
        if (result.status !== 'done') {
          return new ErrorResult(typeof result.data === 'string' && result.data ? result.data : `配置未完成（${result.status}）`, { nodeId })
        }
        // 交付（result.outputs）里带回节点配置后的真实输出字段
        return { nodeId, result: result.data }
      })()
      return { promise, cancel: () => child?.stop() }
    },
  }
}

// ============================================================
// 校验
// ============================================================

function graphOf(lf: LogicFlow) {
  const graph = lf.getGraphData() as LogicFlow.GraphData
  return {
    nodes: graph.nodes.filter((node) => node.type !== WorkflowNodeType.LoopBodyNode),
    edges: graph.edges.filter((edge) => edge.type !== 'loop-edge'),
  } as unknown as ConstructorParameters<typeof WorkFlowInstance>[0]
}

/**
 * 按画布模式选择图结构校验器：工具 / 知识库主画布有各自的开始节点与流程规则。
 * 循环体与 loop-body-node 视图的校验一致：知识库循环用 KnowledgeWorkFlowInstance，其余（含工具循环）用 WorkFlowInstance，
 * 工具循环体的开始节点是 loop-start-node，不能用按 tool-start-node 找开始节点的 ToolWorkFlowInstance。
 */
function instanceOf(mode: WorkflowMode, graph: ReturnType<typeof graphOf>): WorkFlowInstance {
  if (mode === WorkflowMode.Tool) return new ToolWorkFlowInstance(graph, mode)
  if (mode === WorkflowMode.Knowledge || mode === WorkflowMode.KnowledgeLoop) return new KnowledgeWorkFlowInstance(graph, mode)
  return new WorkFlowInstance(graph, mode)
}

export function validateTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'validate',
    description:
      '校验整张工作流：连线完整性（未接入流程的节点、未连接的分支、不能作为结束的节点）、循环体结构与各节点表单必填项；' +
      '工具工作流还检查输出参数是否都有变量赋值写入、是否引用了未声明的输入 / 输出参数。返回 { qualified, problems }。',
    parameters: { type: 'object', properties: {} },
    apply: async () => {
      const problems: string[] = []
      const canvases = await listCanvases(bindings.rootLf, bindings.workflowMode)
      for (const canvas of canvases) {
        const where = canvas.lfId === MAIN_LF_ID ? '主画布' : `循环体(${canvas.lfId})`
        try {
          const instance = instanceOf(canvas.mode, graphOf(canvas.lf))
          if (canvas.lfId === MAIN_LF_ID) instance.is_valid()
          else {
            instance.is_loop_valid()
            const loopNode = canvases.flatMap((item) => item.lf.graphModel.nodes).find((node) => node.id === canvas.lfId)
            if ((loopNode?.properties.node_data as { loop_type?: string } | undefined)?.loop_type === 'LOOP' && !instance.exist_break_node()) {
              problems.push(`${where}：无限循环的循环体需要包含 Break 节点`)
            }
          }
        } catch (error) {
          problems.push(`${where}：${typeof error === 'string' ? error : formatValidationError(error)}`)
        }
        const results = await Promise.allSettled(
          canvas.lf.graphModel.nodes
            .filter((node) => String(node.type) !== WorkflowNodeType.LoopBodyNode)
            .map((node) => (node as unknown as { validate?: () => Promise<unknown> }).validate?.()),
        )
        results.forEach((result) => {
          if (result.status === 'rejected') problems.push(`${where}：${formatValidationError(result.reason)}`)
        })
      }
      if (isToolMode(bindings.workflowMode)) {
        problems.push(...brokenToolParamReferences(bindings.rootLf, canvases))
        unwrittenToolOutputs(bindings.rootLf, canvases).forEach((field) =>
          problems.push(`输出参数 ${field} 没有被写入：需要在产出结果的节点之后接变量赋值节点，target 为 ["output", "${field}"]，否则调用方拿不到该字段`),
        )
      }
      return { qualified: problems.length === 0, problems }
    },
  }
}

export function layoutTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'layout',
    description: '自动整理画布布局（主画布与所有循环体）。',
    parameters: { type: 'object', properties: {} },
    apply: async () => {
      await layoutCanvas(bindings.rootLf)
      return { ok: true }
    },
  }
}
