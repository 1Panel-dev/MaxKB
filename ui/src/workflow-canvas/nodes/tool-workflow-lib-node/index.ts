import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import agent from './agent'
import ToolWorkflowLibNodeDetail from './details/index.vue'
import ToolWorkflowLibNode from './index.vue'

class ToolWorkflowLibNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ToolWorkflowLibNode)
  }
}

export default { type: WorkflowNodeType.ToolWorkflowLib, model: WorkflowNodeModel, view: ToolWorkflowLibNodeView, details: ToolWorkflowLibNodeDetail, agent }
