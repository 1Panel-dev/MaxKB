import StartNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class StartNode extends AppNode {
  constructor(props: any) {
    super(props, StartNodeVue)
  }
}

class StartNodeModel extends AppNodeModel {
  get_width() {
    return 400
  }
}

export default {
  type: 'start-node',
  model: StartNodeModel,
  view: StartNode
}
