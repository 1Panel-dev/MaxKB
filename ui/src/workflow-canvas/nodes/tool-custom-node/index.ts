import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import agent from './agent'
import ToolCustomNodeDetail from './details/index.vue'
import ToolCustomNode from './index.vue'

class ToolCustomNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ToolCustomNode)
  }
}

export default { type: WorkflowNodeType.ToolLibCustom, model: WorkflowNodeModel, view: ToolCustomNodeView, details: ToolCustomNodeDetail, agent }
