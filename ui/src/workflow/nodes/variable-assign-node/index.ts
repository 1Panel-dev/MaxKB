import VariableAssignNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class VariableAssignNode extends AppNode {
  constructor(props: any) {
    super(props, VariableAssignNodeVue)
  }
}

class VariableAssignModel extends AppNodeModel {
  get_width() {
    return 450
  }
}

export default {
  type: 'variable-assign-node',
  model: VariableAssignModel,
  view: VariableAssignNode
}
