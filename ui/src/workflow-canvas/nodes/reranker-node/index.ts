import RerankerNode from './index.vue'
import RerankerNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class RerankerNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, RerankerNode)
  }
}

export default { type: WorkflowNodeType.RerankerNode, model: WorkflowNodeModel, view: RerankerNodeView, details: RerankerNodeDetail }
