import ChatNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/components/workflow/common/app-node/index'
class ChatNode extends AppNode {
  constructor(props: any) {
    super(props, ChatNodeVue)
  }
}
export default {
  type: 'base-node',
  model: AppNodeModel,
  view: ChatNode
}
