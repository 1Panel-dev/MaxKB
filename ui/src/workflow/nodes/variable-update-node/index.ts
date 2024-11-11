import VariableUpdateNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class VariableUpdateNode extends AppNode {
  constructor(props: any) {
    super(props, VariableUpdateNodeVue)
  }
}
export default {
  type: 'variable-update-node',
  model: AppNodeModel,
  view: VariableUpdateNode
}
