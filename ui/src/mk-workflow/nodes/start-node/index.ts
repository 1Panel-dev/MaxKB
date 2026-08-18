import StartNode from './index.vue'
import { AppNode, AppNodeModel } from '@/mk-workflow/core/app-node'
import { WorkflowNodeType } from '@/mk-workflow/types'

class StartNodeView extends AppNode {
  constructor(props: ConstructorParameters<typeof AppNode>[0]) {
    super(props, StartNode)
  }
}

export default {
  type: WorkflowNodeType.Start,
  model: AppNodeModel,
  view: StartNodeView,
}
