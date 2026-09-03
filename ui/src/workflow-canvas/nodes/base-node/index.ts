import BaseNode from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'

class BaseNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, BaseNode)
  }
}

class BaseNodeModel extends WorkflowNodeModel {
  setAttributes() {
    super.setAttributes()
    this.width = 600
  }
}

export default { type: WorkflowNodeType.Base, model: BaseNodeModel, view: BaseNodeView }
