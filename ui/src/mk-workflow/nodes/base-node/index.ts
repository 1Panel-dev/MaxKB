import BaseNode from './index.vue'
import { AppNode, AppNodeModel } from '@/mk-workflow/core/app-node'
import { WorkflowNodeType } from '@/mk-workflow/types'

class BaseNodeView extends AppNode {
  constructor(props: ConstructorParameters<typeof AppNode>[0]) {
    super(props, BaseNode)
  }
}

class BaseNodeModel extends AppNodeModel {
  setAttributes() {
    super.setAttributes()
    this.width = 600
  }
}

export default {
  type: WorkflowNodeType.Base,
  model: BaseNodeModel,
  view: BaseNodeView,
}
