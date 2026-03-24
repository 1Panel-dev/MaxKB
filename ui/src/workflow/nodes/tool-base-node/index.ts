import ToolBaseNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class ToolBaseNode extends AppNode {
  constructor(props: any) {
    super(props, ToolBaseNodeVue)
  }
}
export default {
  type: 'tool-base-node',
  model: AppNodeModel,
  view: ToolBaseNode,
}
