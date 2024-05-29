import ChatNodeVue from '@/workflow/nodes/ai-chat-node/index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node/index'
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
