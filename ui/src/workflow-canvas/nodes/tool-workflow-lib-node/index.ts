import ToolWorkflowLibNode from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class ToolWorkflowLibNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ToolWorkflowLibNode)
  }
}

export default { type: WorkflowNodeType.ToolWorkflowLib, model: WorkflowNodeModel, view: ToolWorkflowLibNodeView }