import FunctionLibNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class FunctionLibNode extends AppNode {
  constructor(props: any) {
    super(props, FunctionLibNodeVue)
  }
}
export default {
  type: 'function-lib-node',
  model: AppNodeModel,
  view: FunctionLibNode
}
