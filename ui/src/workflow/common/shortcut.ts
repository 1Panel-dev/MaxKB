import { cloneDeep } from 'lodash'
import type LogicFlow from '@logicflow/core'
import { type GraphModel } from '@logicflow/core'
import { MsgSuccess, MsgError, MsgConfirm } from '@/utils/message'
import { WorkflowType } from '@/enums/application'
import { t } from '@/locales'
import { copyClick } from '@/utils/clipboard'
import { getMenuNodes, workflowModelDict } from './data'
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
      (node: any) => node.type === WorkflowType.Start || node.type === WorkflowType.Base,
    )
    if (base_nodes.length > 0) {
      MsgError(base_nodes[0]?.properties?.stepName + t('workflow.tip.cannotCopy'))
      return
    }
    selected = cloneDeep(elements)
    selected.nodes.forEach((node: any) => translationNodeData(node, TRANSLATION_DISTANCE))
    selected.edges.forEach((edge: any) => translationEdgeData(edge, TRANSLATION_DISTANCE))
    copyClick(JSON.stringify(selected))
    return false
  }

  const paste_node = async (e: ClipboardEvent) => {
    if (!keyboardOptions?.enabled) return true
    if (graph.textEditElement) return true
    const text = e.clipboardData?.getData('text/plain') || ''
    const data = parseAndValidate(text)
    selected = data
    const workflowMode = lf.graphModel.get_provide(null, null).workflowMode
    const menus = getMenuNodes(workflowMode)
    const nodes = menus?.flatMap((m: any) => m.list).map((n) => n.type)

    if (selected && (selected.nodes || selected.edges)) {
      selected.nodes = selected.nodes.filter(
        (n: any) => nodes?.includes(n.type) || workflowModelDict[workflowMode](n),
      )
      lf.clearSelectElements()
      const addElements = lf.addElements(selected, CHILDREN_TRANSLATION_DISTANCE)
      if (!addElements) return true
      addElements.nodes.forEach((node) => lf.selectElementById(node.id, true))
      addElements.edges.forEach((edge) => lf.selectElementById(edge.id, true))
      selected.nodes.forEach((node: any) => translationNodeData(node, TRANSLATION_DISTANCE))
      selected.edges.forEach((edge: any) => translationEdgeData(edge, TRANSLATION_DISTANCE))
      CHILDREN_TRANSLATION_DISTANCE = CHILDREN_TRANSLATION_DISTANCE + TRANSLATION_DISTANCE
    }
    selected = undefined
    return false
  }

  const parseAndValidate = (text: string) => {
    let data: any
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

    return data
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
        .forEach((edge: any) => lf.deleteEdge(edge.id))
      return
    }
    const nodes = elements.nodes.filter((node) =>
      [
        'start-node',
        'tool-start-node',
        'tool-base-node',
        'base-node',
        'loop-body-node',
        'loop-start-node',
        'knowledge-base-node',
      ].includes(node.type),
    )
    if (nodes.length > 0) {
      MsgError(`${nodes[0].properties?.stepName}${t('workflow.delete.deleteMessage')}`)
      return
    }
    MsgConfirm(t('common.tip'), t('workflow.delete.confirmTitle'), {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger',
    }).then(() => {
      if (!keyboardOptions?.enabled) return true
      if (graph.textEditElement) return true

      elements.edges.forEach((edge: any) => lf.deleteEdge(edge.id))
      elements.nodes.forEach((node: any) => {
        if (node.type === 'loop-node') {
          const next = lf.getNodeOutgoingNode(node.id)
          next.forEach((n: any) => {
            if (n.type === 'loop-body-node') {
              lf.deleteNode(n.id)
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
