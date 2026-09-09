import ParameterExtractionNodeVue from './index.vue'
import ParameterExtractionNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class ParameterExtractionNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ParameterExtractionNodeVue)
  }
}

class ParameterExtractionNodeModel extends WorkflowNodeModel {
  override setAttributes() {
    super.setAttributes()
    this.width = 455
    this.properties.width = 455
  }
}

export default { type: WorkflowNodeType.ParameterExtractionNode, model: ParameterExtractionNodeModel, view: ParameterExtractionNodeView, details: ParameterExtractionNodeDetail }
