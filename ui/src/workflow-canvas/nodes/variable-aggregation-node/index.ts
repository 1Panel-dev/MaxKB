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
    this.width = Number(this.properties.width ?? 450)
    this.height = Number(this.properties.height ?? 300)
    this.text.editable = false
  }
}

export default { type: WorkflowNodeType.VariableAggregationNode, model: VariableAggregationNodeModel, view: VariableAggregationNodeView }
