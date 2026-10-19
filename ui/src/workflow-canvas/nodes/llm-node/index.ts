import LlmNodeVue from './index.vue'
import LlmNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'

class LlmNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, LlmNodeVue)
  }
}

export default {
  type: WorkflowNodeType.Llm,
  model: WorkflowNodeModel,
  view: LlmNodeView,
  details: LlmNodeDetail,
}
