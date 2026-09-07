import LoopBodyNodeVue from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import type { Model } from '@logicflow/core'

class LoopBodyModel extends WorkflowNodeModel {
  setLoopBody?: () => void
  loopLayout?: () => void

  getDefaultAnchor(): Model.AnchorConfig[] {
    return [{ x: this.x, y: this.y - this.height / 2 + 10, id: `${this.id}_children`, type: 'children', edgeAddable: false }]
  }

  refreshBranch() {
    ;[...this.incoming.edges, ...this.outgoing.edges].forEach((edge) => (edge as { updatePathByAnchor?: () => void }).updatePathByAnchor?.())
  }
}

class LoopBodyNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, LoopBodyNodeVue)
  }
}

export default {
  type: WorkflowNodeType.LoopBodyNode,
  model: LoopBodyModel,
  view: LoopBodyNodeView,
}
