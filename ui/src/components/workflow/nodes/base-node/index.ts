import BaseNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/components/workflow/common/app-node/index'
class BaseNode extends AppNode {
  constructor(props: any) {
    super(props, BaseNodeVue)
  }
}
export default {
  type: 'base-node',
  model: AppNodeModel,
  view: BaseNode
}
