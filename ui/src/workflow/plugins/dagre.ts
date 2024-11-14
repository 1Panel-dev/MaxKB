import { DagreLayout, type DagreLayoutOptions } from '@antv/layout'

export default class Dagre {
  static pluginName = 'dagre'
  lf: any
  option: DagreLayoutOptions | any
  render(lf: any) {
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
  layout(option = {}) {
    const { nodes, edges, gridSize } = this.lf.graphModel
    // 为了保证生成的节点在girdSize上，需要处理一下。
    let nodesep = 40
    let ranksep = 40
    if (gridSize > 20) {
      nodesep = gridSize * 2
      ranksep = gridSize * 2
    }
    this.option = {
      type: 'dagre',
      rankdir: 'LR',
      // align: 'UL',
      // align: 'UR',
      align: 'DR',
      nodesep,
      ranksep,
      begin: [120, 120],
      ...option
    }
    const layoutInstance = new DagreLayout(this.option)
    const layoutData = layoutInstance.layout({
      nodes: nodes.map((node: any) => ({
        id: node.id,
        size: {
          width: node.width,
          height: node.height
        },
        model: node
      })),
      edges: edges.map((edge: any) => ({
        source: edge.sourceNodeId,
        target: edge.targetNodeId,
        model: edge
      }))
    })

    layoutData.nodes?.forEach((node: any) => {
      // @ts-ignore: pass node data
      const { model } = node
      model.set_position({ x: node.x, y: node.y })
    })
    this.lf.fitView()
  }
}
