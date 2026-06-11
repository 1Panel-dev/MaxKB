import EmptyNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class EmptyNode extends AppNode {
  constructor(props: any) {
    super(props, EmptyNodeVue)
  }
}

export default {
  type: 'empty-node',
  model: AppNodeModel,
  view: EmptyNode
}
