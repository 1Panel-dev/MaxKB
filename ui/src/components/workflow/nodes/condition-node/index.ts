import ConditioNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/components/workflow/common/app-node/index'
class ConditioNode extends AppNode {
  constructor(props: any) {
    super(props, ConditioNodeVue)
  }
}
export default {
  type: 'condition-node',
  model: AppNodeModel,
  view: ConditioNode
}
