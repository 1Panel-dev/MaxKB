import ContinueNodeNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class ContinueNode extends AppNode {
  constructor(props: any) {
    super(props, ContinueNodeNodeVue)
  }
}

export default {
  type: 'loop-continue-node',
  model: AppNodeModel,
  view: ContinueNode,
}
