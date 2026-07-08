import ReplyNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class ReplyNode extends AppNode {
  constructor(props: any) {
    super(props, ReplyNodeVue)
  }
}
export default {
  type: 'reply-node',
  model: AppNodeModel,
  view: ReplyNode
}
