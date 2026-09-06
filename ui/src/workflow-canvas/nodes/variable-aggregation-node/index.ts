import VariableAggregationNodeVue from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class VariableAggregationNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, VariableAggregationNodeVue)
  }
}

class VariableAggregationNodeModel extends WorkflowNodeModel {
  setAttributes() {
    super.setAttributes()
    this.width = 455
    this.properties.width = 455
    this.text.editable = false
  }
}

export default { type: WorkflowNodeType.VariableAggregationNode, model: VariableAggregationNodeModel, view: VariableAggregationNodeView }
