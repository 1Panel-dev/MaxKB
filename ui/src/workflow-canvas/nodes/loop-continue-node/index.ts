import LoopContinueNodeVue from './index.vue'
import LoopContinueNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class LoopContinueNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, LoopContinueNodeVue)
  }
}

export default {
  type: WorkflowNodeType.LoopContinueNode,
  model: WorkflowNodeModel,
  view: LoopContinueNodeView,
  details: LoopContinueNodeDetail,
}
