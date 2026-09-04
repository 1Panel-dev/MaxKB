import type { BaseNodeModel } from '@logicflow/core'

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

const nodeOverlayStates = new WeakMap<BaseNodeModel, { guards: Set<Set<string>>; hittable: boolean }>()

/**
 * 协调节点内多个非 Teleport 浮层与 SVG 锚点的显隐，避免后绘制的锚点覆盖浮层。
 * 浮层关闭或组件卸载时会恢复节点原本的 hittable 状态。
 */
export function createAnchorGuard(nodeModel: BaseNodeModel) {
  const visibleOverlays = new Set<string>()

  function releaseGuard() {
    const state = nodeOverlayStates.get(nodeModel)
    if (!state || !state.guards.delete(visibleOverlays)) return
    if (state.guards.size === 0) {
      nodeModel.setHittable(state.hittable)
      nodeOverlayStates.delete(nodeModel)
    }
  }

  function setOverlayVisible(overlayKey: string, visible: boolean) {
    if (visible) {
      if (visibleOverlays.has(overlayKey)) return
      let state = nodeOverlayStates.get(nodeModel)
      if (!state) {
        state = { guards: new Set(), hittable: nodeModel.isHittable }
        nodeOverlayStates.set(nodeModel, state)
      }
      visibleOverlays.add(overlayKey)
      state.guards.add(visibleOverlays)
      nodeModel.setHittable(false)
      return
    }

    if (!visibleOverlays.delete(overlayKey)) return
    if (visibleOverlays.size === 0) releaseGuard()
  }

  function reset() {
    if (visibleOverlays.size === 0) return
    visibleOverlays.clear()
    releaseGuard()
  }

  return { reset, setOverlayVisible }
}
