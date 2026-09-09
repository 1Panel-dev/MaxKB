import VariableAssignNodeVue from './index.vue'
import VariableAssignNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class VariableAssignNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, VariableAssignNodeVue)
  }
}

class VariableAssignNodeModel extends WorkflowNodeModel {
  override setAttributes() {
    super.setAttributes()
    this.width = 455
    this.properties.width = 455
  }
}

export default { type: WorkflowNodeType.VariableAssignNode, model: VariableAssignNodeModel, view: VariableAssignNodeView, details: VariableAssignNodeDetail }
