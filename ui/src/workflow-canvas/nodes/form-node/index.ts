import FormNodeVue from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class FormNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, FormNodeVue)
  }
}

export default { type: WorkflowNodeType.FormNode, model: WorkflowNodeModel, view: FormNodeView }
