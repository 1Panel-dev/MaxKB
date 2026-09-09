import DocumentExtractNode from './index.vue'
import DocumentExtractNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class DocumentExtractNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, DocumentExtractNode)
  }
}

export default { type: WorkflowNodeType.DocumentExtractNode, model: WorkflowNodeModel, view: DocumentExtractNodeView, details: DocumentExtractNodeDetail }
