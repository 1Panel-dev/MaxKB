import FunctionNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class FunctionLibCustomNode extends AppNode {
  constructor(props: any) {
    super(props, FunctionNodeVue)
  }
}
export default {
  type: 'function-node',
  model: AppNodeModel,
  view: FunctionLibCustomNode
}
