import ToolCustomNode from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class ToolCustomNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ToolCustomNode)
  }
}

export default { type: WorkflowNodeType.ToolLibCustom, model: WorkflowNodeModel, view: ToolCustomNodeView }
