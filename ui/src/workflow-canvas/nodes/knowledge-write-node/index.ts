import KnowledgeWriteNode from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class KnowledgeWriteNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, KnowledgeWriteNode)
  }
}

export default { type: WorkflowNodeType.KnowledgeWriteNode, model: WorkflowNodeModel, view: KnowledgeWriteNodeView }
