import FormNodeVue from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class FormNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, FormNodeVue)
  }
}

class FormNodeModel extends WorkflowNodeModel {
  override setAttributes() {
    super.setAttributes()
    this.width = 680
    this.properties.width = 680
  }
}

export default { type: WorkflowNodeType.FormNode, model: FormNodeModel, view: FormNodeView }
