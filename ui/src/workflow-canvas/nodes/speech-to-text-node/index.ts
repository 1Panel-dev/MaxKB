import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'
import agent from './agent'
import SpeechToTextNodeDetail from './details/index.vue'
import SpeechToTextNodeVue from './index.vue'

class SpeechToTextNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, SpeechToTextNodeVue)
  }
}

export default {
  type: WorkflowNodeType.SpeechToTextNode,
  model: WorkflowNodeModel,
  view: SpeechToTextNodeView,
  details: SpeechToTextNodeDetail,
  agent,
}
