import StartNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class StartNode extends AppNode {
  constructor(props: any) {
    super(props, StartNodeVue)
  }
}
export default {
  type: 'start-node',
  model: AppNodeModel,
  view: StartNode
}
