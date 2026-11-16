import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'
import StartNodeDetail from './details/index.vue'
import StartNode from './index.vue'

class StartNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, StartNode)
  }
}

export default { type: WorkflowNodeType.Start, model: WorkflowNodeModel, view: StartNodeView, details: StartNodeDetail }
