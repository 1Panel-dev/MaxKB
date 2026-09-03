import ParameterExtractionNodeVue from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class ParameterExtractionNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ParameterExtractionNodeVue)
  }
}

export default { type: WorkflowNodeType.ParameterExtractionNode, model: WorkflowNodeModel, view: ParameterExtractionNodeView }
