import VariableSplittingNodeVue from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class VariableSplittingNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, VariableSplittingNodeVue)
  }
}

export default { type: WorkflowNodeType.VariableSplittingNode, model: WorkflowNodeModel, view: VariableSplittingNodeView }
