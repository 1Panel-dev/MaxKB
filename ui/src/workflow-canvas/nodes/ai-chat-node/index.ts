import AiChatNode from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'

class AiChatNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, AiChatNode)
  }
}

export default {
  type: WorkflowNodeType.AiChat,
  model: WorkflowNodeModel,
  view: AiChatNodeView,
}
