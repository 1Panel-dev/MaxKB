import ChatNodeVue from '@/flow/nodes/ai-chat-node/index.vue'
import { AppNode, AppNodeModel } from '@/flow/common/app-node/index'
class ChatNode extends AppNode {
  constructor(props: any) {
    super(props, ChatNodeVue)
  }
}
export default {
  type: 'ai-chat-node',
  model: AppNodeModel,
  view: ChatNode
}
