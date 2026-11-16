import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import agent from './agent'
import VariableSplittingNodeDetail from './details/index.vue'
import VariableSplittingNodeVue from './index.vue'

class VariableSplittingNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, VariableSplittingNodeVue)
  }
}

class VariableSplittingNodeModel extends WorkflowNodeModel {
  override setAttributes() {
    super.setAttributes()
    this.width = 455
    this.properties.width = 455
  }
}

export default { type: WorkflowNodeType.VariableSplittingNode, model: VariableSplittingNodeModel, view: VariableSplittingNodeView, details: VariableSplittingNodeDetail, agent }
