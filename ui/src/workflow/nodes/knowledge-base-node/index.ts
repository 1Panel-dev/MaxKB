import BaseNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class BaseNode extends AppNode {
  constructor(props: any) {
    super(props, BaseNodeVue)
  }
}

class BaseModel extends AppNodeModel {
  constructor(data: any, graphModel: any) {
    super(data, graphModel)
  }
  get_width() {
    return 600
  }
}
export default {
  type: 'knowledge-base-node',
  model: BaseModel,
  view: BaseNode,
}
