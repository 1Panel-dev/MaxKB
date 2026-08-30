import ReplyNode from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'

class ReplyNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ReplyNode)
  }
}

export default { type: WorkflowNodeType.Reply, model: WorkflowNodeModel, view: ReplyNodeView }
