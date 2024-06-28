import type LogicFlow from '@logicflow/core'
import { type GraphModel } from '@logicflow/core'
import { MsgSuccess, MsgError, MsgConfirm } from '@/utils/message'
import { WorkflowType } from '@/enums/workflow'
let selected: any | null = null

function translationNodeData(nodeData: any, distance: any) {
  nodeData.x += distance
  nodeData.y += distance
  if (nodeData.text) {
    nodeData.text.x += distance
    nodeData.text.y += distance
  }
  return nodeData
}

function translationEdgeData(edgeData: any, distance: any) {
  if (edgeData.startPoint) {
    edgeData.startPoint.x += distance
    edgeData.startPoint.y += distance
  }
  if (edgeData.endPoint) {
    edgeData.endPoint.x += distance
    edgeData.endPoint.y += distance
  }
  if (edgeData.pointsList && edgeData.pointsList.length > 0) {
    edgeData.pointsList.forEach((point: any) => {
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
  const { keyboard } = lf
  const {
    options: { keyboard: keyboardOptions }
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
      (node: any) => node.type === WorkflowType.Start || node.type === WorkflowType.Base
    )
    if (base_nodes.length > 0) {
      MsgError(base_nodes[0]?.properties?.stepName + '不能被复制')
      return
    }
    selected = elements
    selected.nodes.forEach((node: any) => translationNodeData(node, TRANSLATION_DISTANCE))
    selected.edges.forEach((edge: any) => translationEdgeData(edge, TRANSLATION_DISTANCE))
    MsgSuccess('已复制节点')
    return false
  }
  const paste_node = () => {
    if (!keyboardOptions?.enabled) return true
    if (graph.textEditElement) return true
    if (selected && (selected.nodes || selected.edges)) {
      lf.clearSelectElements()
      console.log(selected)
      const addElements = lf.addElements(selected, CHILDREN_TRANSLATION_DISTANCE)
      if (!addElements) return true
      addElements.nodes.forEach((node) => lf.selectElementById(node.id, true))
      addElements.edges.forEach((edge) => lf.selectElementById(edge.id, true))
      selected.nodes.forEach((node: any) => translationNodeData(node, TRANSLATION_DISTANCE))
      selected.edges.forEach((edge: any) => translationEdgeData(edge, TRANSLATION_DISTANCE))
      CHILDREN_TRANSLATION_DISTANCE = CHILDREN_TRANSLATION_DISTANCE + TRANSLATION_DISTANCE
    }
    return false
  }
  const delete_node = () => {
    const elements = graph.getSelectElements(true)
    lf.clearSelectElements()
    if (elements.nodes.length == 0 && elements.edges.length == 0) {
      return
    }
    if (elements.edges.length > 0 && elements.nodes.length == 0) {
      elements.edges.forEach((edge: any) => lf.deleteEdge(edge.id))
      return
    }
    const nodes = elements.nodes.filter((node) => ['start-node', 'base-node'].includes(node.type))
    if (nodes.length > 0) {
      MsgError(`${nodes[0].properties?.stepName}节点不允许删除`)
      return
    }
    MsgConfirm(`提示`, `确定删除该节点？`, {
      confirmButtonText: '删除',
      confirmButtonClass: 'danger'
    }).then(() => {
      if (!keyboardOptions?.enabled) return true
      if (graph.textEditElement) return true

      elements.edges.forEach((edge: any) => lf.deleteEdge(edge.id))
      elements.nodes.forEach((node: any) => lf.deleteNode(node.id))
    })

    return false
  }
  graph.eventCenter.on('copy_node', copy_node)
  // 复制
  keyboard.on(['cmd + c', 'ctrl + c'], copy_node)
  // 粘贴
  keyboard.on(['cmd + v', 'ctrl + v'], paste_node)
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
