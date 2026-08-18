import AiChatNode from './index.vue'
import { AppNode, AppNodeModel } from '@/mk-workflow/core/app-node'
import { WorkflowNodeType } from '@/mk-workflow/types'

class AiChatNodeView extends AppNode {
  constructor(props: ConstructorParameters<typeof AppNode>[0]) {
    super(props, AiChatNode)
  }
}

export default {
  type: WorkflowNodeType.AiChat,
  model: AppNodeModel,
  view: AiChatNodeView,
}
