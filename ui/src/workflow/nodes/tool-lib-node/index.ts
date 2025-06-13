import ToolLibNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class ToolLibNode extends AppNode {
  constructor(props: any) {
    super(props, ToolLibNodeVue)
  }
}
export default {
  type: 'tool-lib-node',
  model: AppNodeModel,
  view: ToolLibNode,
}
