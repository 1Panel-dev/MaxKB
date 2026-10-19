import { nextTick, reactive } from 'vue'
import { cloneDeep } from 'lodash'
import type LogicFlow from '@logicflow/core'
import type { BaseNodeModel, Model } from '@logicflow/core'
import type { ModelConfig } from '@/api/types'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { getMenuNodes } from '@/workflow-canvas/node-menu/menu'
import { WorkflowMode, WorkflowNodeType, type ShapeItem, type WorkflowNodeField } from '@/workflow-canvas/types'

/**
 * MaxKB 画布适配层：AI 生成通过这里读写 LogicFlow 图，屏蔽主画布 / 循环体画布的差异。
 * 画布用 lf_id 标识：主画布为 "main"，循环体为所属循环节点的 id。
 */

export const MAIN_LF_ID = 'main'

/** 画布固定节点：不可新增、删除或由 AI 配置 */
export const FIXED_NODE_TYPES: string[] = [
  WorkflowNodeType.Base,
  WorkflowNodeType.Start,
  WorkflowNodeType.LoopStartNode,
  WorkflowNodeType.LoopBodyNode,
]

type LoopBodyModel = BaseNodeModel & { getLoopLogicFlow?: () => LogicFlow | null; loopLayout?: () => unknown }
type BranchNodeData = { branch?: Array<{ id: string; type?: string; content?: string; isOther?: boolean }> }
type DagreExtension = { dagre?: { layout?: () => Promise<unknown> | unknown } }

export interface CanvasRef {
  lf: LogicFlow
  lfId: string
  mode: WorkflowMode
  /** 循环层深（主画布为 -1，最外层循环体为 0） */
  depth: number
}

export interface OutgoingAnchor {
  anchorId: string
  label: string
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export function loopModeOf(mode: WorkflowMode): WorkflowMode {
  if (mode === WorkflowMode.Knowledge) return WorkflowMode.KnowledgeLoop
  if (mode === WorkflowMode.Tool) return WorkflowMode.ToolLoop
  return WorkflowMode.ApplicationLoop
}

export function getNode(lf: LogicFlow, nodeId: string): WorkflowNodeModel | undefined {
  return (lf.graphModel.getNodeModelById(nodeId) as unknown as WorkflowNodeModel | undefined) ?? undefined
}

export function nodeNameOf(node: BaseNodeModel): string {
  return String(node.properties.stepName ?? node.type)
}

/** 取循环节点挂载的循环体画布；循环体在 Vue 挂载后才创建，最多等待 3 秒 */
export async function getLoopBodyLf(lf: LogicFlow, loopNodeId: string): Promise<LogicFlow | null> {
  for (let attempt = 0; attempt < 30; attempt++) {
    const body = lf.graphModel.getNodeOutgoingNode(loopNodeId).find((node) => String(node.type) === WorkflowNodeType.LoopBodyNode) as
      | LoopBodyModel
      | undefined
    const bodyLf = body?.getLoopLogicFlow?.()
    if (bodyLf) return bodyLf
    await sleep(100)
  }
  return null
}

/** 广度遍历主画布及所有已展开的循环体画布 */
export async function listCanvases(rootLf: LogicFlow, rootMode: WorkflowMode): Promise<CanvasRef[]> {
  const canvases: CanvasRef[] = [{ lf: rootLf, lfId: MAIN_LF_ID, mode: rootMode, depth: -1 }]
  for (let index = 0; index < canvases.length; index++) {
    const canvas = canvases[index]!
    for (const node of canvas.lf.graphModel.nodes) {
      if (String(node.type) !== WorkflowNodeType.LoopNode) continue
      const bodyLf = await getLoopBodyLf(canvas.lf, node.id)
      if (bodyLf) canvases.push({ lf: bodyLf, lfId: node.id, mode: loopModeOf(rootMode), depth: canvas.depth + 1 })
    }
  }
  return canvases
}

/** 按 lf_id 取画布；循环 id 会在所有层级里查找 */
export async function resolveCanvas(rootLf: LogicFlow, rootMode: WorkflowMode, lfId?: string): Promise<CanvasRef | { error: string }> {
  const target = !lfId || lfId === MAIN_LF_ID ? MAIN_LF_ID : lfId
  const canvas = (await listCanvases(rootLf, rootMode)).find((item) => item.lfId === target)
  if (canvas) return canvas
  return { error: `找不到画布 lf_id=${lfId}：主画布传 "main"，循环体传所属循环节点 id（循环节点需处于展开状态）` }
}

/** 按节点 id 在所有画布中定位节点所在画布 */
export async function findNodeCanvas(rootLf: LogicFlow, rootMode: WorkflowMode, nodeId: string): Promise<CanvasRef | undefined> {
  return (await listCanvases(rootLf, rootMode)).find((canvas) => !!getNode(canvas.lf, nodeId))
}

/** 节点在当前画布模式下可新增时返回菜单模板 */
export function findNodeTemplate(mode: WorkflowMode, type: string): ShapeItem | undefined {
  return getMenuNodes(mode)
    .flatMap((group) => group.list)
    .find((node) => node.type === type)
}

/**
 * 写回节点属性。节点视图拿到的是 reactive(model)，经同一代理写入才能触发 Vue 表单刷新。
 */
export function writeNodeProperties(node: BaseNodeModel, properties: Record<string, unknown>) {
  const reactiveNode = reactive(node) as BaseNodeModel
  Object.entries(properties).forEach(([key, value]) => {
    reactiveNode.properties[key] = value
  })
}

export function readNodeData<T>(node: BaseNodeModel): T {
  return cloneDeep((node.properties.node_data ?? {}) as T)
}

/** 节点的输出口：判断器 / 意图识别按分支，其余为正常输出与（开启时的）异常输出 */
export function getOutgoingAnchors(node: BaseNodeModel): OutgoingAnchor[] {
  const nodeData = node.properties.node_data as BranchNodeData | undefined
  if (String(node.type) === WorkflowNodeType.Condition) {
    return (nodeData?.branch ?? []).map((branch) => ({ anchorId: `${node.id}_${branch.id}_right`, label: `分支 ${branch.type ?? branch.id}` }))
  }
  if (String(node.type) === WorkflowNodeType.IntentNode) {
    return (nodeData?.branch ?? []).map((branch) => ({
      anchorId: `${node.id}_${branch.id}_right`,
      label: `分类 ${branch.isOther ? '其他' : branch.content || branch.id}`,
    }))
  }
  return (node.getDefaultAnchor() as Model.AnchorConfig[])
    .filter((anchor) => anchor.type === 'right')
    .map((anchor) => ({ anchorId: String(anchor.id), label: String(anchor.id).endsWith('_exception_right') ? '异常输出' : '正常输出' }))
}

/** 把上游节点 id 或完整出口锚点 id 解析成出口；不存在时返回错误文本 */
export function resolveSourceAnchor(lf: LogicFlow, source: string): { node: WorkflowNodeModel; anchorId: string } | { error: string } {
  const direct = getNode(lf, source)
  if (direct) {
    const anchors = getOutgoingAnchors(direct)
    if (anchors.length === 1 || [WorkflowNodeType.Condition, WorkflowNodeType.IntentNode].every((type) => type !== String(direct.type))) {
      const anchor = anchors.find((item) => item.anchorId === `${direct.id}_right`) ?? anchors[0]
      if (anchor) return { node: direct, anchorId: anchor.anchorId }
    }
    return { error: `节点 ${source} 有多个分支出口，请先 get_node_anchors 取具体出口的 source_anchor_id` }
  }
  const owner = lf.graphModel.nodes.find((node) => source.startsWith(`${node.id}_`))
  if (owner && getOutgoingAnchors(owner).some((anchor) => anchor.anchorId === source)) {
    return { node: owner as unknown as WorkflowNodeModel, anchorId: source }
  }
  return { error: `出口不存在: ${source}（普通连接传上游节点 id，分支出口用 get_node_anchors 查询）` }
}

/** 判断器与意图识别的锚点依赖 branch_condition_list，写入分支后按 id 同步，保证新出口立即可连线 */
export function refreshBranchAnchors(node: BaseNodeModel) {
  const nodeData = node.properties.node_data as BranchNodeData | undefined
  if (String(node.type) === WorkflowNodeType.Condition) {
    const previous = (node.properties.branch_condition_list as Array<{ id: string; height: number }> | undefined) ?? []
    writeNodeProperties(node, {
      branch_condition_list: (nodeData?.branch ?? []).map((branch, index) => ({
        id: branch.id,
        index,
        height: previous.find((item) => item.id === branch.id)?.height ?? 44,
      })),
    })
  }
  ;(node as BaseNodeModel & { refreshBranch?: () => void }).refreshBranch?.()
}

export function addEdge(lf: LogicFlow, sourceNodeId: string, sourceAnchorId: string, targetNodeId: string): string | null {
  if (sourceNodeId === targetNodeId) return '不能连接到自身'
  const duplicated = lf.graphModel.edges.some((edge) => edge.sourceAnchorId === sourceAnchorId && edge.targetNodeId === targetNodeId)
  if (duplicated) return null
  lf.graphModel.addEdge({
    type: 'app-edge',
    sourceNodeId,
    sourceAnchorId,
    targetNodeId,
    targetAnchorId: `${targetNodeId}_left`,
  })
  getNode(lf, targetNodeId)?.clearNextNodeField(true)
  return null
}

/** 新节点放在上游右侧，按上游已有出边数纵向错开，避免重叠；最终由自动布局整理 */
export function addNode(
  lf: LogicFlow,
  template: ShapeItem,
  sourceNodeId: string,
  propertiesOverride: Record<string, unknown> = {},
): WorkflowNodeModel {
  const source = getNode(lf, sourceNodeId)
  const outgoingCount = source ? lf.graphModel.getNodeOutgoingEdge(sourceNodeId).length : 0
  const x = (source?.x ?? 400) + (source?.width ?? 320) / 2 + 400
  const y = (source?.y ?? 400) + outgoingCount * 420
  const node = lf.graphModel.addNode({
    type: String(template.type),
    properties: { ...cloneDeep(template.properties ?? {}), ...propertiesOverride },
    x,
    y,
  })
  return node as unknown as WorkflowNodeModel
}

export function getDefaultModelConfig(lf: LogicFlow, modelType: string): ModelConfig | undefined {
  const graphModel = lf.graphModel as LogicFlow['graphModel'] & { getDefaultModelSettings?: () => Partial<Record<string, ModelConfig>> | undefined }
  return graphModel.getDefaultModelSettings?.()?.[modelType]
}

/** 自动布局：先整理各循环体，再整理主画布 */
export async function layoutCanvas(rootLf: LogicFlow) {
  await nextTick()
  try {
    await Promise.all(
      rootLf.graphModel.nodes
        .filter((node) => String(node.type) === WorkflowNodeType.LoopBodyNode)
        .map((node) => (node as LoopBodyModel).loopLayout?.()),
    )
    await nextTick()
    await (rootLf.extension as DagreExtension).dagre?.layout?.()
  } catch {
    // 布局失败不影响生成结果
  }
}

// ============================================================
// 上游字段与引用
// ============================================================

export interface FieldOptionGroup {
  /** 引用路径第一段：节点 id，或 global / chat / loop 等分组 */
  nodeId: string
  /** 节点名称（提示词变量 {{节点名称.字段}} 使用） */
  name: string
  fields: Array<{ value: string; label: string }>
}

/** 与 NodeCascader 一致的可引用字段：开始节点、全局/会话变量、上游节点；循环体内追加父画布字段 */
export function getFieldOptions(lf: LogicFlow, nodeId: string): FieldOptionGroup[] {
  const node = getNode(lf, nodeId)
  if (!node) return []
  const graphModel = lf.graphModel as LogicFlow['graphModel'] & {
    getUpNodeFieldList?: (containSelf: boolean, useCache: boolean) => WorkflowNodeField[]
  }
  const groups = [...node.getUpNodeFieldList(false, false), ...(graphModel.getUpNodeFieldList?.(false, false) ?? [])]
  const seen = new Set<string>()
  return groups
    .filter((group) => group.children?.length && !seen.has(group.value) && seen.add(group.value))
    .map((group) => ({
      nodeId: group.value,
      name: group.label,
      fields: (group.children ?? []).map((field) => ({ value: field.value, label: field.label })),
    }))
}

/** 校验 [节点ID, 字段] 引用是否在上游可引用字段内；合法返回 null */
export function validateReference(lf: LogicFlow, nodeId: string, reference: unknown, label = '引用'): string | null {
  if (!Array.isArray(reference) || reference.length < 2) return `${label} 应为 [节点ID, 字段] 形式`
  const [refNodeId, field] = reference.map(String)
  const group = getFieldOptions(lf, nodeId).find((item) => item.nodeId === refNodeId)
  if (!group) return `${label} 引用的节点 ${refNodeId} 不在上游，先 get_field_options 查可引用的节点`
  if (!group.fields.some((item) => item.value === field)) {
    return `${label} 引用的字段 ${refNodeId}.${field} 不存在，可用字段：${group.fields.map((item) => item.value).join(', ')}`
  }
  return null
}

/** 提示词变量：{{节点名称.字段}}，全局变量为 {{global.字段}} */
export function promptVariablesOf(lf: LogicFlow, nodeId: string): string[] {
  return getFieldOptions(lf, nodeId).flatMap((group) =>
    group.fields.map((field) => (group.nodeId === 'global' ? `{{global.${field.value}}}` : `{{${group.name}.${field.value}}}`)),
  )
}

/** 检查提示词里的 {{…}} 变量是否都可解析；合法返回 null */
export function validatePromptVariables(lf: LogicFlow, nodeId: string, text: unknown, label: string): string | null {
  if (typeof text !== 'string') return null
  const available = new Set(promptVariablesOf(lf, nodeId))
  const invalid = [...text.matchAll(/\{\{[^{}]+\}\}/g)].map((match) => match[0]).filter((variable) => !available.has(variable))
  if (!invalid.length) return null
  return `${label} 中的变量 ${invalid.join('、')} 无法解析，可用变量：${[...available].join('、') || '无'}`
}

/** 节点输出字段（config.fields） */
export function nodeOutputFields(node: BaseNodeModel): Array<{ value: string; label: string }> {
  const config = node.properties.config as { fields?: Array<{ value: string; label: string }> } | undefined
  return (config?.fields ?? []).map((field) => ({ value: field.value, label: field.label }))
}
