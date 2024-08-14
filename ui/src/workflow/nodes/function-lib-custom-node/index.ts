import FunctionLibCustomNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class FunctionLibCustomNode extends AppNode {
  constructor(props: any) {
    super(props, FunctionLibCustomNodeVue)
  }
}
export default {
  type: 'function-lib-custom-node',
  model: AppNodeModel,
  view: FunctionLibCustomNode
}
