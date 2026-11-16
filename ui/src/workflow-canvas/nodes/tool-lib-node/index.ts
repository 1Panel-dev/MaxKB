import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import agent from './agent'
import ToolLibNodeDetail from './details/index.vue'
import ToolLibNode from './index.vue'

class ToolLibNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ToolLibNode)
  }
}

export default { type: WorkflowNodeType.ToolLib, model: WorkflowNodeModel, view: ToolLibNodeView, details: ToolLibNodeDetail, agent }
