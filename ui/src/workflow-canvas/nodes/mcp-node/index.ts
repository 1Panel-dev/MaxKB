import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import agent from './agent'
import McpNodeDetail from './details/index.vue'
import McpNodeVue from './index.vue'

class McpNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, McpNodeVue)
  }
}

export default { type: WorkflowNodeType.McpNode, model: WorkflowNodeModel, view: McpNodeView, details: McpNodeDetail, agent }
