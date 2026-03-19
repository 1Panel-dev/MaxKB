import VariableAggregationNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class VariableAggregationNode extends AppNode {
  constructor(props: any) {
    super(props, VariableAggregationNodeVue)
  }
  getConfig(props: any) {
    return props.model.properties.config
  }
}

class VariableAggregationNodeModel extends AppNodeModel {
  get_width() {
    return 450
  }
}

export default {
  type: 'variable-aggregation-node',
  model: VariableAggregationNodeModel,
  view: VariableAggregationNode,
}
