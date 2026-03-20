import VariableAssignNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class VariableAssignNode extends AppNode {
  constructor(props: any) {
    super(props, VariableAssignNodeVue)
  }
}

export default {
  type: 'variable-assign-node',
  model: AppNodeModel,
  view: VariableAssignNode
}
