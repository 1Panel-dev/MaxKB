import BreakNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class BreakNode extends AppNode {
  constructor(props: any) {
    super(props, BreakNodeVue)
  }
}

export default {
  type: 'loop-break-node',
  model: AppNodeModel,
  view: BreakNode,
}
