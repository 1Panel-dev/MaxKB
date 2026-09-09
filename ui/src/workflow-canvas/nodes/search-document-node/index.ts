import SearchDocumentNode from './index.vue'
import SearchDocumentNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class SearchDocumentNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, SearchDocumentNode)
  }
}

class SearchDocumentNodeModel extends WorkflowNodeModel {
  override setAttributes() {
    super.setAttributes()
    this.width = 455
    this.properties.width = 455
  }
}

export default { type: WorkflowNodeType.SearchDocument, model: SearchDocumentNodeModel, view: SearchDocumentNodeView, details: SearchDocumentNodeDetail }
