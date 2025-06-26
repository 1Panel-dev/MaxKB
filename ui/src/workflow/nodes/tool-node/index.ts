import ToolNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class ToolLibCustomNode extends AppNode {
  constructor(props: any) {
    super(props, ToolNodeVue)
  }
}
export default {
  type: 'tool-node',
  model: AppNodeModel,
  view: ToolLibCustomNode,
}
