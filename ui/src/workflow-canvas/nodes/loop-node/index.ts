import type { Model } from '@logicflow/core'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import agent from './agent'
import LoopNodeDetail from './details/index.vue'
import LoopNodeVue from './index.vue'

class LoopNodeModel extends WorkflowNodeModel {
  getDefaultAnchor(): Model.AnchorConfig[] {
    const anchors = super.getDefaultAnchor()
    anchors.push({ x: this.x, y: this.y + this.height / 2, id: `${this.id}_children`, type: 'children', edgeAddable: false })
    return anchors
  }

  refreshBranch() {
    ;[...this.incoming.edges, ...this.outgoing.edges].forEach((edge) => (edge as { updatePathByAnchor?: () => void }).updatePathByAnchor?.())
  }
}

class LoopNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, LoopNodeVue)
  }
}

export default {
  type: WorkflowNodeType.LoopNode,
  model: LoopNodeModel,
  view: LoopNodeView,
  details: LoopNodeDetail,
  agent,
}
