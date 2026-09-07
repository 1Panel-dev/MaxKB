import SearchDocumentNode from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class SearchDocumentNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, SearchDocumentNode)
  }
}

export default { type: WorkflowNodeType.SearchDocument, model: WorkflowNodeModel, view: SearchDocumentNodeView }
