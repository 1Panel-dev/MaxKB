import SpeechToTextNodeVue from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'

class SpeechToTextNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, SpeechToTextNodeVue)
  }
}

export default {
  type: WorkflowNodeType.SpeechToTextNode,
  model: WorkflowNodeModel,
  view: SpeechToTextNodeView,
}
