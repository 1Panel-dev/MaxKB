import McpNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class McpNode extends AppNode {
  constructor(props: any) {
    super(props, McpNodeVue)
  }
}

export default {
  type: 'mcp-node',
  model: AppNodeModel,
  view: McpNode
}
