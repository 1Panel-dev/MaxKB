import ParameterExtractionNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class ParameterExtractionNode extends AppNode {
  constructor(props: any) {
    super(props, ParameterExtractionNodeVue)
  }
  getConfig(props: any) {
    return props.model.properties.config
  }
}

export default {
  type: 'parameter-extraction-node',
  model: AppNodeModel,
  view: ParameterExtractionNode,
}
