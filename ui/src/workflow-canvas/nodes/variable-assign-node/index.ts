import VariableAssignNodeVue from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class VariableAssignNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, VariableAssignNodeVue)
  }
}

export default { type: WorkflowNodeType.VariableAssignNode, model: WorkflowNodeModel, view: VariableAssignNodeView }
