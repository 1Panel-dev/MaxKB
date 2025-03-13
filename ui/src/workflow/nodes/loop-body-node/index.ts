import LoopNode from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
import { WorkflowType } from '@/enums/workflow'
class LoopBodyNodeView extends AppNode {
  constructor(props: any) {
    super(props, LoopNode)
  }
}
class LoopBodyModel extends AppNodeModel {
  refreshBranch() {
    // 更新节点连接边的path
    this.incoming.edges.forEach((edge: any) => {
      // 调用自定义的更新方案
      edge.updatePathByAnchor()
    })
    this.outgoing.edges.forEach((edge: any) => {
      edge.updatePathByAnchor()
    })
  }
  getDefaultAnchor() {
    const { id, x, y, width, height } = this
    const showNode = this.properties.showNode === undefined ? true : this.properties.showNode
    const anchors: any = []
    anchors.push({
      edgeAddable: false,
      x: x,
      y: y - height / 2 + 10,
      id: `${id}_children`,
      type: 'children'
    })

    return anchors
  }
}
export default {
  type: 'loop-body-node',
  model: LoopBodyModel,
  view: LoopBodyNodeView
}
