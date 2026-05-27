import ToolBaseNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class ToolBaseNode extends AppNode {
  constructor(props: any) {
    super(props, ToolBaseNodeVue)
  }
}

class ToolBaseNodeModel extends AppNodeModel {
  get_width() {
    return 600
  }
}

export default {
  type: 'tool-base-node',
  model: ToolBaseNodeModel,
  view: ToolBaseNode,
}
