import ToolBaseNode from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'

class ToolBaseNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ToolBaseNode)
  }
}

class ToolBaseNodeModel extends WorkflowNodeModel {
  setAttributes() {
    super.setAttributes()
    this.width = 600
  }
}

export default { type: WorkflowNodeType.ToolBaseNode, model: ToolBaseNodeModel, view: ToolBaseNodeView }