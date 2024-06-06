import ChatNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node.ts'
class ChatNode extends AppNode {
  constructor(props: any) {
    super(props, ChatNodeVue)
  }
}
export default {
  type: 'start-node',
  model: AppNodeModel,
  view: ChatNode
}
