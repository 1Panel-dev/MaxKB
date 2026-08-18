import type LogicFlow from '@logicflow/core'
import type { GraphModel } from '@logicflow/core'
import { cloneDeep } from 'lodash'
import { getMenuNodes, workflowModelDict, defaultNodes } from '@/mk-workflow/core/data'
import { WorkflowMode, WorkflowNodeType } from '@/mk-workflow/types'
import { copyText } from '@/utils/clipboard'
import { MsgConfirm, MsgError } from '@/utils/message'

type WorkflowGraphModel = GraphModel & {
  get_provide: (
    node: LogicFlow.NodeData | null,
    graph: GraphModel | null,
  ) => { workflowMode: WorkflowMode }
}

const TRANSLATION_DISTANCE = 40
const fixedNodeTypes = new Set<string>([
  WorkflowNodeType.Start,
  WorkflowNodeType.ToolStartNode,
  WorkflowNodeType.ToolBaseNode,
  WorkflowNodeType.Base,
  WorkflowNodeType.LoopBodyNode,
  WorkflowNodeType.LoopStartNode,
  WorkflowNodeType.KnowledgeBase,
])

let activeCanvasId: string | null = null
let childrenTranslationDistance = TRANSLATION_DISTANCE
let selectedGraphData: LogicFlow.GraphData | null = null

const lastMousePosition = {
  x: 0,
  y: 0,
  hasValue: false,
}

function bindMousePosition(logicFlow: LogicFlow) {
  const updateMousePosition = (event: MouseEvent) => {
    lastMousePosition.x = event.clientX
    lastMousePosition.y = event.clientY
    lastMousePosition.hasValue = true
  }

  logicFlow.container.addEventListener('mousemove', updateMousePosition)
  return () => logicFlow.container.removeEventListener('mousemove', updateMousePosition)
}

function bindCanvasActive(logicFlow: LogicFlow) {
  const { container } = logicFlow
  container.tabIndex = 0

  const activateCanvas = () => {
    activeCanvasId = logicFlow.graphModel.flowId ?? null
    container.focus()
  }

  container.addEventListener('mousedown', activateCanvas)
  container.addEventListener('focus', activateCanvas)
  return () => {
    container.removeEventListener('mousedown', activateCanvas)
    container.removeEventListener('focus', activateCanvas)
  }
}

function translateNodeData(nodeData: LogicFlow.NodeData, distance: number) {
  nodeData.x += distance
  nodeData.y += distance
  if (nodeData.text) {
    nodeData.text.x += distance
    nodeData.text.y += distance
  }
}

function translateEdgeData(edgeData: LogicFlow.EdgeData, distance: number) {
  edgeData.startPoint.x += distance
  edgeData.startPoint.y += distance
  edgeData.endPoint.x += distance
  edgeData.endPoint.y += distance
  edgeData.pointsList?.forEach((point) => {
    point.x += distance
    point.y += distance
  })
  if (edgeData.text) {
    edgeData.text.x += distance
    edgeData.text.y += distance
  }
}

function translateGraphData(graphData: LogicFlow.GraphData, offsetX: number, offsetY: number) {
  graphData.nodes.forEach((node) => {
    node.x += offsetX
    node.y += offsetY
  })
  graphData.edges.forEach((edge) => {
    edge.startPoint.x += offsetX
    edge.startPoint.y += offsetY
    edge.endPoint.x += offsetX
    edge.endPoint.y += offsetY
    if (edge.text) {
      edge.text.x += offsetX
      edge.text.y += offsetY
    }
    edge.pointsList = edge.pointsList?.map((point) => ({
      ...point,
      x: point.x + offsetX,
      y: point.y + offsetY,
    }))
  })
}

function getNodeBounds(nodes: LogicFlow.NodeData[]) {
  const firstNode = nodes[0]
  if (!firstNode) return { minX: 0, maxX: 0, minY: 0, maxY: 0 }

  return nodes.reduce(
    (bounds, node) => ({
      minX: Math.min(bounds.minX, node.x),
      maxX: Math.max(bounds.maxX, node.x),
      minY: Math.min(bounds.minY, node.y),
      maxY: Math.max(bounds.maxY, node.y),
    }),
    { minX: firstNode.x, maxX: firstNode.x, minY: firstNode.y, maxY: firstNode.y },
  )
}

function createGraphElementId() {
  return crypto.randomUUID()
}

function resetGraphDataIds(graphData: LogicFlow.GraphData) {
  const idMap = new Map<string, string>()
  const replaceId = (oldId: string) => {
    const existingId = idMap.get(oldId)
    if (existingId) return existingId
    const newId = createGraphElementId()
    idMap.set(oldId, newId)
    return newId
  }

  graphData.nodes.forEach((node) => {
    node.id = replaceId(node.id)
  })
  graphData.edges.forEach((edge) => {
    const oldSourceNodeId = edge.sourceNodeId
    const oldTargetNodeId = edge.targetNodeId
    edge.id = replaceId(edge.id)
    edge.sourceNodeId = replaceId(oldSourceNodeId)
    edge.targetNodeId = replaceId(oldTargetNodeId)
    if (edge.sourceAnchorId) {
      edge.sourceAnchorId = edge.sourceAnchorId.replace(oldSourceNodeId, edge.sourceNodeId)
    }
    if (edge.targetAnchorId) {
      edge.targetAnchorId = edge.targetAnchorId.replace(oldTargetNodeId, edge.targetNodeId)
    }
  })
  return graphData
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function parseGraphData(text: string): LogicFlow.GraphData {
  let parsedData: unknown
  try {
    parsedData = JSON.parse(text)
  } catch {
    throw new Error('数据不是合法的 JSON')
  }

  if (!isRecord(parsedData)) throw new Error('数据必须是对象')
  if (!Array.isArray(parsedData.nodes)) throw new Error('nodes 必须是数组')
  if (!Array.isArray(parsedData.edges)) throw new Error('edges 必须是数组')

  parsedData.nodes.forEach((node, index) => {
    if (!isRecord(node)) throw new Error(`nodes[${index}] 必须是对象`)
    if (typeof node.id !== 'string' || !node.id) throw new Error(`nodes[${index}] 缺少 id`)
  })
  parsedData.edges.forEach((edge, index) => {
    if (!isRecord(edge)) throw new Error(`edges[${index}] 必须是对象`)
    if (typeof edge.id !== 'string' || !edge.id) throw new Error(`edges[${index}] 缺少 id`)
  })

  return parsedData as unknown as LogicFlow.GraphData
}

export function initDefaultShortcut(logicFlow: LogicFlow, graphModel: GraphModel) {
  const unbindMousePosition = bindMousePosition(logicFlow)
  const unbindCanvasActive = bindCanvasActive(logicFlow)
  const { keyboard } = logicFlow
  const keyboardEnabled = () => keyboard.options.keyboard?.enabled === true

  const copyNode = () => {
    childrenTranslationDistance = TRANSLATION_DISTANCE
    if (!keyboardEnabled() || graphModel.textEditElement) return true

    const selectedElements = graphModel.getSelectElements(false)
    const cloneAllowed = logicFlow.options.guards?.beforeClone?.(selectedElements) ?? true
    if (
      !cloneAllowed ||
      (selectedElements.nodes.length === 0 && selectedElements.edges.length === 0)
    ) {
      selectedGraphData = null
      return true
    }

    const fixedNode = selectedElements.nodes.find((node) => fixedNodeTypes.has(node.type))
    if (fixedNode) {
      MsgError(`${String(fixedNode.properties?.stepName ?? fixedNode.type)}不能被复制`)
      return true
    }

    selectedGraphData = cloneDeep(selectedElements)
    selectedGraphData.nodes.forEach((node) => translateNodeData(node, TRANSLATION_DISTANCE))
    selectedGraphData.edges.forEach((edge) => translateEdgeData(edge, TRANSLATION_DISTANCE))
    void copyText(JSON.stringify(selectedGraphData))
    return false
  }

  const pasteNode = (event: ClipboardEvent) => {
    if (logicFlow.graphModel.flowId !== activeCanvasId) return true
    if (!keyboardEnabled() || graphModel.textEditElement) return true

    const clipboardText = event.clipboardData?.getData('text/plain') ?? ''
    const graphData = resetGraphDataIds(parseGraphData(clipboardText))
    selectedGraphData = graphData

    const workflowMode = (logicFlow.graphModel as WorkflowGraphModel).get_provide(
      null,
      null,
    ).workflowMode
    const menuNodeTypes = getMenuNodes(workflowMode)
      ?.flatMap((menuGroup) => menuGroup.list)
      .map((node) => node.type)

    if (!lastMousePosition.hasValue) {
      translateGraphData(graphData, TRANSLATION_DISTANCE, TRANSLATION_DISTANCE)
    } else {
      const { canvasOverlayPosition } = logicFlow.graphModel.getPointByClient({
        x: lastMousePosition.x,
        y: lastMousePosition.y,
      })
      const { minX, maxX, minY, maxY } = getNodeBounds(graphData.nodes)
      translateGraphData(
        graphData,
        canvasOverlayPosition.x - (minX + maxX) / 2,
        canvasOverlayPosition.y - (minY + maxY) / 2,
      )
    }

    const workflowNodeMatcher = workflowModelDict[workflowMode]
    graphData.nodes = graphData.nodes.filter(
      (node) => menuNodeTypes?.includes(node.type as WorkflowNodeType) || workflowNodeMatcher(node),
    )

    logicFlow.clearSelectElements()
    const addedElements = logicFlow.addElements(graphData, childrenTranslationDistance)
    addedElements.nodes.forEach((node) => logicFlow.selectElementById(node.id, true))
    addedElements.edges.forEach((edge) => logicFlow.selectElementById(edge.id, true))
    selectedGraphData.nodes.forEach((node) => translateNodeData(node, TRANSLATION_DISTANCE))
    selectedGraphData.edges.forEach((edge) => translateEdgeData(edge, TRANSLATION_DISTANCE))
    childrenTranslationDistance += TRANSLATION_DISTANCE
    selectedGraphData = null
    return false
  }

  const deleteNode = () => {
    const selectedElements = graphModel.getSelectElements(true)
    logicFlow.clearSelectElements()
    if (!selectedElements.nodes.length && !selectedElements.edges.length) return true

    if (selectedElements.edges.length && !selectedElements.nodes.length) {
      selectedElements.edges
        .filter((edge) => edge.type !== 'loop-edge')
        .forEach((edge) => logicFlow.deleteEdge(edge.id))
      return false
    }

    const fixedNode = selectedElements.nodes.find((node) => fixedNodeTypes.has(node.type))
    if (fixedNode) {
      MsgError(`${String(fixedNode.properties?.stepName ?? fixedNode.type)}节点不允许删除`)
      return true
    }

    void MsgConfirm('提示', '确定要删除吗？', {
      confirmButtonText: '确认',
      confirmButtonClass: 'danger',
    }).then(() => {
      if (!keyboardEnabled() || graphModel.textEditElement) return
      selectedElements.edges.forEach((edge) => logicFlow.deleteEdge(edge.id))
      selectedElements.nodes.forEach((node) => {
        if (node.type === WorkflowNodeType.LoopNode) {
          logicFlow
            .getNodeOutgoingNode(node.id)
            .filter((nextNode) => String(nextNode.type) === WorkflowNodeType.LoopBodyNode)
            .forEach((nextNode) => logicFlow.deleteNode(nextNode.id))
        }
        logicFlow.deleteNode(node.id)
      })
    })
    return false
  }

  graphModel.eventCenter.on('copy_node', copyNode)
  keyboard.on(['cmd + c', 'ctrl + c'], copyNode)
  keyboard.on(['cmd + v', 'ctrl + v'], () => undefined)
  keyboard.on(['cmd + z', 'ctrl + z'], () => undefined)
  keyboard.on(['cmd + y', 'ctrl + y'], () => {
    if (keyboardEnabled() && !graphModel.textEditElement) logicFlow.redo()
  })
  keyboard.on('backspace', deleteNode)
  document.addEventListener('paste', pasteNode)

  return () => {
    unbindMousePosition()
    unbindCanvasActive()
    document.removeEventListener('paste', pasteNode)
    graphModel.eventCenter.off('copy_node', copyNode)
    keyboard.off(['cmd + c', 'ctrl + c'])
    keyboard.off(['cmd + v', 'ctrl + v'])
    keyboard.off(['cmd + z', 'ctrl + z'])
    keyboard.off(['cmd + y', 'ctrl + y'])
    keyboard.off('backspace')
  }
}
