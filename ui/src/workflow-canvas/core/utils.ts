export function isWorkFlow(type: string | undefined) {
  return type === 'WORK_FLOW'
}

export function handleNodeWheel(event: WheelEvent) {
  if (event.ctrlKey) {
    event.preventDefault()
    return true
  } else {
    event.stopPropagation()
    return true
  }
}

export function isLastNode(nodeModel: BaseNodeModel) {
  const incoming = nodeModel.graphModel.getNodeIncomingNode(nodeModel.id)
  const outcomming = nodeModel.graphModel.getNodeOutgoingNode(nodeModel.id)
  if (incoming.length > 0 && outcomming.length === 0) {
    return true
  } else {
    return false
  }
}
import type { BaseNodeModel } from '@logicflow/core'
