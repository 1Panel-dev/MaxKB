import type LogicFlow from '@logicflow/core'
import type { BaseEdgeModel, BaseNodeModel } from '@logicflow/core'
import { DagreLayout, type DagreLayoutOptions } from '@antv/layout'

type DagreNodeData = { id: string; model: BaseNodeModel; size: { height: number; width: number } }

type DagreEdgeData = { id: string; model: BaseEdgeModel; source: string; target: string }

export default class Dagre {
  static pluginName = 'dagre'

  lf?: LogicFlow

  render(lf: LogicFlow) {
    this.lf = lf
  }

  /**
   * option: {
   *   rankdir: "TB", // layout 方向, 可选 TB, BT, LR, RL
   *   align: undefined, // 节点对齐方式，可选 UL, UR, DL, DR
   *   nodeSize: undefined, // 节点大小
   *   nodesepFunc: undefined, // 节点水平间距(px)
   *   ranksepFunc: undefined, // 每一层节点之间间距
   *   nodesep: 40, // 节点水平间距(px) 注意：如果有grid，需要保证nodesep为grid的偶数倍
   *   ranksep: 40, // 每一层节点之间间距 注意：如果有grid，需要保证ranksep为grid的偶数倍
   *   controlPoints: false, // 是否保留布局连线的控制点
   *   radial: false, // 是否基于 dagre 进行辐射布局
   *   focusNode: null, // radial 为 true 时生效，关注的节点
   * };
   */

  async layout(options: Partial<DagreLayoutOptions> = {}) {
    if (!this.lf) return
    const { edges, gridSize, nodes } = this.lf.graphModel
    const defaultSpacing = gridSize > 20 ? gridSize * 2 : 40
    const layoutOptions: Partial<DagreLayoutOptions> = {
      type: 'dagre',
      rankdir: 'LR',
      align: 'DR',
      nodesep: defaultSpacing,
      ranksep: defaultSpacing,
      begin: [120, 120],
      nodeSize: (node) => {
        const { model } = node as DagreNodeData
        return [model.width, model.height]
      },
      ...options,
    }

    const layoutInstance = new DagreLayout(layoutOptions)
    await layoutInstance.execute({
      nodes: nodes.map<DagreNodeData>((node) => ({ id: node.id, size: { width: node.width, height: node.height }, model: node })),
      edges: edges.map<DagreEdgeData>((edge) => ({ id: edge.id, source: edge.sourceNodeId, target: edge.targetNodeId, model: edge })),
    })
    // moveTo 只改节点坐标、不带动连线，需经 graphModel 移动才会同步边的端点
    layoutInstance.forEachNode((node) => {
      const { model } = node._original as DagreNodeData
      this.lf?.graphModel.moveNode2Coordinate(model.id, node.x, node.y, true)
    })
    // 按锚点重算连线路径，清掉布局前的折点
    edges.forEach((edge) => (edge as BaseEdgeModel & { updatePathByAnchor?: () => void }).updatePathByAnchor?.())
    this.lf.fitView()
  }
}
