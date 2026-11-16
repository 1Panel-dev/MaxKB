import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'
import agent from './agent'
import ReplyNodeDetail from './details/index.vue'
import ReplyNode from './index.vue'

class ReplyNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ReplyNode)
  }
}

export default { type: WorkflowNodeType.Reply, model: WorkflowNodeModel, view: ReplyNodeView, details: ReplyNodeDetail, agent }
