import ToolWorkflowLibNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class ToolWorkflowLibNode extends AppNode {
  constructor(props: any) {
    super(props, ToolWorkflowLibNodeVue)
  }
}
export default {
  type: 'tool-workflow-lib-node',
  model: AppNodeModel,
  view: ToolWorkflowLibNode,
}
