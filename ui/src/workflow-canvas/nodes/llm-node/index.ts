import LlmNodeVue from './index.vue'
import LlmNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'

class LlmNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, LlmNodeVue)
  }
}

class LlmNodeModel extends WorkflowNodeModel {
  override setAttributes() {
    super.setAttributes()
    this.width = 600
    this.properties.width = 600
  }
}

export default {
  type: WorkflowNodeType.Llm,
  model: LlmNodeModel,
  view: LlmNodeView,
  details: LlmNodeDetail,
}
