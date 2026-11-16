import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'
import agent from './agent'
import TextToVideoNodeDetail from './details/index.vue'
import TextToVideoNodeVue from './index.vue'

class TextToVideoNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, TextToVideoNodeVue)
  }
}

export default {
  type: WorkflowNodeType.TextToVideoGenerateNode,
  model: WorkflowNodeModel,
  view: TextToVideoNodeView,
  details: TextToVideoNodeDetail,
  agent,
}
