import LoopBreakNodeVue from './index.vue'
import LoopBreakNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class LoopBreakNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, LoopBreakNodeVue)
  }
}

export default {
  type: WorkflowNodeType.LoopBreakNode,
  model: WorkflowNodeModel,
  view: LoopBreakNodeView,
  details: LoopBreakNodeDetail,
}
