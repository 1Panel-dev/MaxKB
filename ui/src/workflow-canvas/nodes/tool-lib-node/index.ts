import ToolLibNode from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class ToolLibNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ToolLibNode)
  }
}

export default { type: WorkflowNodeType.ToolLib, model: WorkflowNodeModel, view: ToolLibNodeView }
