import { cloneDeep } from 'lodash'
import type LogicFlow from '@logicflow/core'
import { type GraphModel } from '@logicflow/core'
import { MsgError, MsgConfirm } from '@/utils/message'
import { WorkflowMode, WorkflowNodeType } from '@/workflow-canvas/types'
import { copyText } from '@/utils/clipboard'
import { randomId } from '@/utils/common'
import { workflowModelDict } from '@/workflow-canvas/config/node-mapping'
import { getMenuNodes } from '@/workflow-canvas/config/menu'
let activeCanvasId: string | null = null
type Point = { x: number; y: number }
type WorkflowGraphModel = GraphModel & {
  get_provide: (
    node: LogicFlow.NodeData | null,
    graph: GraphModel | null,
  ) => { workflowMode: WorkflowMode }
}

const lastMouse = {
  x: 0,
  y: 0,
  hasValue: false,
}
let selected: LogicFlow.GraphData | null = null
const bindMousePosition = (lf: LogicFlow) => {
  const updateMouse = (e: MouseEvent) => {
    lastMouse.x = e.clientX
    lastMouse.y = e.clientY
    lastMouse.hasValue = true
  }

  // 推荐直接监听容器，这样鼠标在节点上移动也能拿到
  lf.container.addEventListener('mousemove', updateMouse)

  return () => {
    lf.container.removeEventListener('mousemove', updateMouse)
  }
}
const bindCanvasActive = (lf: LogicFlow) => {
  const container = lf.container
  if (!container) return

  // 让容器可聚焦
  container.tabIndex = 0

  const activate = () => {
    activeCanvasId = lf.graphModel.flowId ?? null
    container.focus()
  }

  container.addEventListener('mousedown', activate)
  container.addEventListener('focus', activate)

  return () => {
    container.removeEventListener('mousedown', activate)
    container.removeEventListener('focus', activate)
  }
}
function translationNodeData(nodeData: LogicFlow.NodeData, distance: number) {
  nodeData.x += distance
  nodeData.y += distance
  if (nodeData.text) {
    nodeData.text.x += distance
    nodeData.text.y += distance
  }
  return nodeData
}

function translationEdgeData(edgeData: LogicFlow.EdgeData, distance: number) {
  if (edgeData.startPoint) {
    edgeData.startPoint.x += distance
    edgeData.startPoint.y += distance
  }
  if (edgeData.endPoint) {
    edgeData.endPoint.x += distance
    edgeData.endPoint.y += distance
  }
  if (edgeData.pointsList && edgeData.pointsList.length > 0) {
    edgeData.pointsList.forEach((point) => {
      point.x += distance
      point.y += distance
    })
  }
  if (edgeData.text) {
    edgeData.text.x += distance
    edgeData.text.y += distance
  }
  return edgeData
}

const TRANSLATION_DISTANCE = 40
let CHILDREN_TRANSLATION_DISTANCE = 40

export function initDefaultShortcut(lf: LogicFlow, graph: GraphModel) {
  bindMousePosition(lf)
  bindCanvasActive(lf)
  const { keyboard } = lf
  const {
    options: { keyboard: keyboardOptions },
  } = keyboard
  const copy_node = () => {
    CHILDREN_TRANSLATION_DISTANCE = TRANSLATION_DISTANCE
    if (!keyboardOptions?.enabled) return true
    if (graph.textEditElement) return true
    const { guards } = lf.options
    const elements = graph.getSelectElements(false)
    const enabledClone = guards && guards.beforeClone ? guards.beforeClone(elements) : true
    if (!enabledClone || (elements.nodes.length === 0 && elements.edges.length === 0)) {
      selected = null
      return true
    }
    const base_nodes = elements.nodes.filter(
      (node) => node.type === WorkflowNodeType.Start || node.type === WorkflowNodeType.Base,
    )
    if (base_nodes.length > 0) {
      MsgError(base_nodes[0]?.properties?.stepName + '不能被复制')
      return
    }
    selected = cloneDeep(elements)
    selected.nodes.forEach((node) => translationNodeData(node, TRANSLATION_DISTANCE))
    selected.edges.forEach((edge) => translationEdgeData(edge, TRANSLATION_DISTANCE))
    copyText(JSON.stringify(selected))
    return false
  }
  // 3. 求节点包围盒
  const getBounds = (nodes: LogicFlow.NodeData[]) => {
    if (!nodes.length) {
      return { minX: 0, maxX: 0, minY: 0, maxY: 0 }
    }

    const firstNode = nodes[0]!
    let minX = firstNode.x
    let maxX = firstNode.x
    let minY = firstNode.y
    let maxY = firstNode.y

    for (const node of nodes) {
      if (node.x < minX) minX = node.x
      if (node.x > maxX) maxX = node.x
      if (node.y < minY) minY = node.y
      if (node.y > maxY) maxY = node.y
    }

    return { minX, maxX, minY, maxY }
  }

  // 4. 整体平移
  const moveData = (data: LogicFlow.GraphData, dx: number, dy: number) => {
    for (const node of data.nodes ?? []) {
      node.x += dx
      node.y += dy
    }

    for (const edge of data.edges ?? []) {
      if (edge.startPoint) {
        edge.startPoint.x += dx
        edge.startPoint.y += dy
      }
      if (edge.endPoint) {
        edge.endPoint.x += dx
        edge.endPoint.y += dy
      }
      if (edge.text && typeof edge.text.x === 'number' && typeof edge.text.y === 'number') {
        edge.text.x += dx
        edge.text.y += dy
      }
      if (Array.isArray(edge.pointsList)) {
        edge.pointsList = edge.pointsList.map((p: Point) => ({
          ...p,
          x: p.x + dx,
          y: p.y + dy,
        }))
      }
    }
  }
  const resetData = (data: LogicFlow.GraphData) => {
    const idMap = new Map<string, string>()

    const getOrCreateId = (oldId: string) => {
      let newId = idMap.get(oldId)
      if (!newId) {
        newId = randomId()
        idMap.set(oldId, newId)
      }
      return newId
    }

    for (const node of data.nodes) {
      node.id = getOrCreateId(node.id)
    }

    for (const edge of data.edges) {
      const oldEdgeId = edge.id
      const oldSourceNodeId = edge.sourceNodeId
      const oldTargetNodeId = edge.targetNodeId

      edge.id = getOrCreateId(oldEdgeId)
      edge.sourceNodeId = getOrCreateId(oldSourceNodeId)
      edge.targetNodeId = getOrCreateId(oldTargetNodeId)

      if (typeof edge.sourceAnchorId === 'string') {
        edge.sourceAnchorId = edge.sourceAnchorId.replace(oldSourceNodeId, edge.sourceNodeId)
      }

      if (typeof edge.targetAnchorId === 'string') {
        edge.targetAnchorId = edge.targetAnchorId.replace(oldTargetNodeId, edge.targetNodeId)
      }
    }

    return data
  }

  const paste_node = async (e: ClipboardEvent) => {
    if (lf.graphModel.flowId !== activeCanvasId) {
      return true
    }
    if (!keyboardOptions?.enabled) return true
    if (graph.textEditElement) return true
    const text = e.clipboardData?.getData('text/plain') || ''
    const data = parseAndValidate(text)
    selected = resetData(data)
    const workflowMode = (lf.graphModel as WorkflowGraphModel).get_provide(null, null).workflowMode
    const menus = getMenuNodes(workflowMode)
    const menuNodeTypes = new Set(menus?.flatMap((menu) => menu.list).map((node) => node.type))

    if (selected && (selected.nodes || selected.edges)) {
      if (!lastMouse.hasValue) {
        moveData(data, 40, 40)
      } else {
        // LogicFlow 文档里 getPointByClient 会把页面坐标转成画布坐标
        const point = lf.graphModel.getPointByClient({
          x: lastMouse.x,
          y: lastMouse.y,
        })
        const mouseCanvasX = point.canvasOverlayPosition.x
        const mouseCanvasY = point.canvasOverlayPosition.y

        const { minX, maxX, minY, maxY } = getBounds(selected.nodes)
        const centerX = (minX + maxX) / 2
        const centerY = (minY + maxY) / 2
        moveData(data, mouseCanvasX - centerX, mouseCanvasY - centerY)
      }

      selected.nodes = selected.nodes.filter(
        (node) =>
          menuNodeTypes.has(node.type as WorkflowNodeType) || workflowModelDict[workflowMode](node),
      )
      lf.clearSelectElements()
      const addElements = lf.addElements(selected, CHILDREN_TRANSLATION_DISTANCE)
      if (!addElements) return true
      addElements.nodes.forEach((node) => lf.selectElementById(node.id, true))
      addElements.edges.forEach((edge) => lf.selectElementById(edge.id, true))
      selected.nodes.forEach((node) => translationNodeData(node, TRANSLATION_DISTANCE))
      selected.edges.forEach((edge) => translationEdgeData(edge, TRANSLATION_DISTANCE))
      CHILDREN_TRANSLATION_DISTANCE = CHILDREN_TRANSLATION_DISTANCE + TRANSLATION_DISTANCE
    }
    selected = null
    return false
  }

  const parseAndValidate = (text: string) => {
    let data: unknown
    try {
      data = JSON.parse(text)
    } catch {
      throw new Error('数据不是合法的 JSON')
    }

    if (!data || typeof data !== 'object' || Array.isArray(data)) {
      throw new Error('数据必须是对象')
    }

    if (!('nodes' in data)) {
      throw new Error('数据缺少 nodes 字段')
    }

    if (!('edges' in data)) {
      throw new Error('数据缺少 edges 字段')
    }

    if (!Array.isArray(data.nodes)) {
      throw new Error('nodes 必须是数组')
    }

    for (let i = 0; i < data.nodes.length; i++) {
      const node = data.nodes[i]

      if (!node || typeof node !== 'object' || Array.isArray(node)) {
        throw new Error(`nodes[${i}] 必须是对象`)
      }

      if (!('id' in node) || node.id === undefined || node.id === null || node.id === '') {
        throw new Error(`nodes[${i}] 缺少 id`)
      }
    }

    return data as LogicFlow.GraphData
  }
  document.addEventListener('paste', paste_node)

  const delete_node = () => {
    const elements = graph.getSelectElements(true)
    lf.clearSelectElements()
    if (elements.nodes.length == 0 && elements.edges.length == 0) {
      return
    }
    if (elements.edges.length > 0 && elements.nodes.length == 0) {
      elements.edges
        .filter((edge) => !['loop-edge'].includes(edge.type || ''))
        .forEach((edge) => lf.deleteEdge(edge.id))
      return
    }
    const protectedNodeTypes: string[] = [
      WorkflowNodeType.Start,
      WorkflowNodeType.ToolStartNode,
      WorkflowNodeType.ToolBaseNode,
      WorkflowNodeType.Base,
      WorkflowNodeType.LoopBodyNode,
      WorkflowNodeType.LoopStartNode,
      WorkflowNodeType.KnowledgeBase,
    ]
    const nodes = elements.nodes.filter((node) => protectedNodeTypes.includes(node.type))
    if (nodes.length > 0) {
      MsgError(`${nodes[0]?.properties?.stepName}节点不允许删除`)
      return
    }
    MsgConfirm('提示', '确定删除选中的节点和连线吗？', {
      confirmButtonText: '确定',
      confirmButtonClass: 'danger',
    }).then(() => {
      if (!keyboardOptions?.enabled) return true
      if (graph.textEditElement) return true

      elements.edges.forEach((edge) => lf.deleteEdge(edge.id))
      elements.nodes.forEach((node) => {
        if (node.type === WorkflowNodeType.LoopNode) {
          const next = lf.getNodeOutgoingNode(node.id)
          next.forEach((nextNode) => {
            if (String(nextNode.type) === WorkflowNodeType.LoopBodyNode) {
              lf.deleteNode(nextNode.id)
            }
          })
        }
        lf.deleteNode(node.id)
      })
    })

    return false
  }
  graph.eventCenter.on('copy_node', copy_node)
  // 复制
  keyboard.on(['cmd + c', 'ctrl + c'], copy_node)
  // 粘贴
  keyboard.on(['cmd + v', 'ctrl + v'], () => {})
  // undo
  keyboard.on(['cmd + z', 'ctrl + z'], () => {
    // if (!keyboardOptions?.enabled) return true
    // if (graph.textEditElement) return true
    // lf.undo()
    // return false
  })
  // redo
  keyboard.on(['cmd + y', 'ctrl + y'], () => {
    if (!keyboardOptions?.enabled) return true
    if (graph.textEditElement) return true
    lf.redo()
    return false
  })
  // delete
  keyboard.on(['backspace'], delete_node)
}
