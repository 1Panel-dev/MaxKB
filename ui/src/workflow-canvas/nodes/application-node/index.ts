import ApplicationNode from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class ApplicationNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ApplicationNode)
  }
}

export default { type: WorkflowNodeType.Application, model: WorkflowNodeModel, view: ApplicationNodeView }
