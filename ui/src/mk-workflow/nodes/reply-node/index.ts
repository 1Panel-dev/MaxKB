import ReplyNode from './index.vue'
import { AppNode, AppNodeModel } from '@/mk-workflow/core/app-node'
import { WorkflowNodeType } from '@/mk-workflow/types'

class ReplyNodeView extends AppNode {
  constructor(props: ConstructorParameters<typeof AppNode>[0]) {
    super(props, ReplyNode)
  }
}

export default {
  type: WorkflowNodeType.Reply,
  model: AppNodeModel,
  view: ReplyNodeView,
}
