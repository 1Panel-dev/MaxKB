import ConditioNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node.ts'
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
