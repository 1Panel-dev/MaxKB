import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'
import agent from './agent'
import TextToSpeechNodeDetail from './details/index.vue'
import TextToSpeechNodeVue from './index.vue'

class TextToSpeechNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, TextToSpeechNodeVue)
  }
}

export default {
  type: WorkflowNodeType.TextToSpeechNode,
  model: WorkflowNodeModel,
  view: TextToSpeechNodeView,
  details: TextToSpeechNodeDetail,
  agent,
}
