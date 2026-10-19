import { cloneDeep } from 'lodash'
import { TOOL_TYPE } from '@/api/enums'
import type LogicFlow from '@logicflow/core'
import { WorkFlowInstance } from '@/workflow-canvas/core/validate'
import { toolLibNode } from '@/workflow-canvas/config/node-data'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode, WorkflowNodeType, type ShapeItem } from '@/workflow-canvas/types'
import {
  FIXED_NODE_TYPES,
  MAIN_LF_ID,
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
import { formatValidationError, isReference, summarizeNodeData } from './node'
import { ErrorResult } from './result'
import type { AgentBindings, AgentTool, JsonSchema, NodeAgentModule, NodeReference } from '../type'


/** 节点配置 agent 取自各节点 index.ts 默认导出的 agent 字段；未提供的节点不进入 AI 可选目录 */
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

function describeCanvas(canvas: CanvasRef) {
  const nodes = canvas.lf.graphModel.nodes.filter((node) => String(node.type) !== WorkflowNodeType.LoopBodyNode)
  return {
    lf_id: canvas.lfId,
    nodes: nodes.map((node) => ({
      id: node.id,
      type: String(node.type),
      name: nodeNameOf(node),
      outputs: nodeOutputFields(node).map((field) => field.value),
      node_data: summarizeNodeData(node.properties.node_data),
    })),
    edges: canvas.lf.graphModel.edges
      .filter((edge) => edge.type !== 'loop-edge')
      .map((edge) => {
        const source = canvas.lf.graphModel.getNodeModelById(edge.sourceNodeId)
        const label = source ? getOutgoingAnchors(source).find((anchor) => anchor.anchorId === edge.sourceAnchorId)?.label : undefined
        return { source_anchor_id: edge.sourceAnchorId, from: edge.sourceNodeId, outlet: label, to: edge.targetNodeId }
      }),
  }
}

async function canvasOrError(bindings: AgentBindings, lfId: unknown) {
  return resolveCanvas(bindings.rootLf, bindings.workflowMode, typeof lfId === 'string' ? lfId : undefined)
}

export function getCanvasDetailTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'get_canvas_detail',
    description: '查看整张工作流现状：主画布与各循环体（loopBodies[循环节点id]）的节点（id/type/name/输出字段/配置摘要）与连线。',
    parameters: { type: 'object', properties: {} },
    resultLimit: 20000,
    apply: async () => {
      const canvases = await listCanvases(bindings.rootLf, bindings.workflowMode)
      const [main, ...loops] = canvases
      return { main: describeCanvas(main!), loopBodies: Object.fromEntries(loops.map((canvas) => [canvas.lfId, describeCanvas(canvas)])) }
    },
  }
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

/** 工具节点的模板：按工具详情补齐参数与名称，与资源菜单拖入的节点一致 */
async function toolNodeTemplate(bindings: AgentBindings, toolId: string): Promise<ShapeItem | { error: string }> {
  const tool = await useWorkflowStore(bindings.resourceScope)
    .force.getToolById(toolId)
    .catch(() => null)
  if (!tool?.id) return { error: `工具不存在: ${toolId}` }
  const inputFields = (tool.input_field_list ?? []).map((field) => ({ ...field, value: field.source === 'reference' ? [] : '' }))
  return {
    ...cloneDeep(toolLibNode),
    properties: {
      ...cloneDeep(toolLibNode.properties),
      stepName: tool.name,
      node_data: { ...cloneDeep(tool), input_field_list: inputFields, tool_lib_id: tool.id },
    },
  }
}

/** 列出可在应用工作流中使用的自定义工具（父 agent 选型用） */
export function getToolsTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'get_tools',
    description: '列出可用的自定义工具 [{id,name,desc,inputs:[{name,type,source,is_required,desc}]}]，add_node 新增 tool-lib-node 时传其 tool_id。',
    parameters: { type: 'object', properties: {} },
    apply: async () => {
      const tools = await useWorkflowStore(bindings.resourceScope).getToolListWithShared({ tool_type: TOOL_TYPE.CUSTOM })
      return tools
        .filter((tool) => tool.is_active && tool.tool_type === TOOL_TYPE.CUSTOM)
        .map((tool) => ({
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
    },
  }
}

export function addNodeTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'add_node',
    description:
      '新增节点并从上游出口接一条入边（建即接，杜绝孤立节点）。source_anchor_id：普通连接传上游节点 id；接判断器/意图识别某分支时传 get_node_anchors 返回的出口 id。' +
      '循环体首个节点接 "loop-start-node"。tool-lib-node 需同时传 tool_id（get_tools 查询）。返回 { nodeId, name, outputs }。',
    parameters: {
      type: 'object',
      properties: {
        type: { type: 'string', description: '节点类型（节点目录中的 type）' },
        source_anchor_id: { type: 'string', description: '上游节点 id 或出口 id' },
        name: { type: 'string', description: '节点名称（可选，体现用途，如 "产品知识检索"）' },
        tool_id: { type: 'string', description: 'type=tool-lib-node 时必填' },
        lf_id: LF_ID_SCHEMA,
      },
      required: ['type', 'source_anchor_id'],
    },
    apply: async (args) => {
      const canvas = await canvasOrError(bindings, args.lf_id)
      if ('error' in canvas) return canvas
      const type = String(args.type)
      if (FIXED_NODE_TYPES.includes(type)) return { error: `${type} 是画布固定节点，不能新增` }
      if (!nodeAgentFor(type)) return { error: `暂不支持 AI 生成 ${type}，请从节点目录中选择` }
      let template: ShapeItem | { error: string } | undefined
      if (type === WorkflowNodeType.ToolLib) {
        if (!args.tool_id) return { error: 'tool-lib-node 需要 tool_id，先 get_tools 查询' }
        template = await toolNodeTemplate(bindings, String(args.tool_id))
      } else {
        template = findNodeTemplate(canvas.mode, type)
      }
      if (!template) {
        return {
          error:
            canvas.mode === WorkflowMode.ApplicationLoop ? `循环体内不能使用 ${type}` : `主画布不能使用 ${type}（Break/Continue 只能建在循环体内）`,
        }
      }
      if ('error' in template) return template
      const source = resolveSourceAnchor(canvas.lf, String(args.source_anchor_id))
      if ('error' in source) return source
      const node = addNode(canvas.lf, template, source.node.id, args.name ? { stepName: String(args.name) } : {})
      const error = addEdge(canvas.lf, source.node.id, source.anchorId, node.id)
      if (error) return { error }
      return { nodeId: node.id, name: nodeNameOf(node), lf_id: canvas.lfId, outputs: nodeOutputFields(node) }
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
      if ([...FIXED_NODE_TYPES].includes(String(target.type))) return { error: '固定节点不能作为连线终点' }
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
      if (FIXED_NODE_TYPES.includes(String(node.type))) return { error: '固定节点不能删除' }
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
    // 带 items 的 array 形参可接收多个引用（如提示词素材、重排内容），其余形参只接收一个引用
    const multiple = schema.type === 'array' && schema.items !== undefined
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
        if (!module) return new ErrorResult(`${node.type} 暂不支持 AI 配置`, { nodeId })
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
          module.useAgent({ lf: canvas.lf, nodeId, workflowMode: canvas.mode, bindings: childBindings, args: checked.args, requirement, expectedReturns }),
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

export function validateTool(bindings: AgentBindings): AgentTool {
  return {
    name: 'validate',
    description:
      '校验整张工作流：连线完整性（未接入流程的节点、未连接的分支、不能作为结束的节点）、循环体结构与各节点表单必填项。返回 { qualified, problems }。',
    parameters: { type: 'object', properties: {} },
    apply: async () => {
      const problems: string[] = []
      const canvases = await listCanvases(bindings.rootLf, bindings.workflowMode)
      for (const canvas of canvases) {
        const where = canvas.lfId === MAIN_LF_ID ? '主画布' : `循环体(${canvas.lfId})`
        try {
          const instance = new WorkFlowInstance(graphOf(canvas.lf), canvas.mode)
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
