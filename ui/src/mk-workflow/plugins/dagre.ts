import type LogicFlow from '@logicflow/core'
import type { BaseNodeModel } from '@logicflow/core'
import { DagreLayout, type DagreLayoutOptions } from '@antv/layout'

type LayoutNode = {
  id: string
  model: BaseNodeModel
}

type LayoutEdge = {
  id: string
  source: string
  target: string
}

export default class Dagre {
  static pluginName = 'dagre'

  private logicFlow?: LogicFlow

  render(logicFlow: LogicFlow) {
    this.logicFlow = logicFlow
  }

  async layout(options: Partial<DagreLayoutOptions> = {}) {
    const logicFlow = this.logicFlow
    if (!logicFlow) return

    const { edges, gridSize, nodes } = logicFlow.graphModel
    const defaultSpacing = gridSize > 20 ? gridSize * 2 : 40
    const layoutOptions: Partial<DagreLayoutOptions> = {
      rankdir: 'LR',
      align: 'DR',
      nodesep: defaultSpacing,
      ranksep: defaultSpacing,
      nodeSize: (node) => {
        const { model } = node as LayoutNode
        return [model.width, model.height]
      },
      node: (node) => ({ id: (node as LayoutNode).id }),
      edge: (edge) => {
        const layoutEdge = edge as LayoutEdge
        return {
          id: layoutEdge.id,
          source: layoutEdge.source,
          target: layoutEdge.target,
        }
      },
      ...options,
    }
    const layoutInstance = new DagreLayout(layoutOptions)
    await layoutInstance.execute({
      nodes: nodes.map((node) => ({ id: node.id, model: node })),
      edges: edges.map((edge) => ({
        id: edge.id,
        source: edge.sourceNodeId,
        target: edge.targetNodeId,
      })),
    })
    layoutInstance.forEachNode((node) => {
      const { model } = node._original as LayoutNode
      model.moveTo(node.x, node.y)
    })
    logicFlow.fitView()
  }
}
