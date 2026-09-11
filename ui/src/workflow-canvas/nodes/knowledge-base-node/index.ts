import KnowledgeBaseNode from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class KnowledgeBaseNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, KnowledgeBaseNode)
  }
}

class KnowledgeBaseNodeModel extends WorkflowNodeModel {
  setAttributes() {
    super.setAttributes()
    this.width = 600
  }
}

export default { type: WorkflowNodeType.KnowledgeBase, model: KnowledgeBaseNodeModel, view: KnowledgeBaseNodeView }
