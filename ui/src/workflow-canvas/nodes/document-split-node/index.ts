import DocumentSplitNode from './index.vue'
import DocumentSplitNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class DocumentSplitNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, DocumentSplitNode)
  }
}

class DocumentSplitNodeModel extends WorkflowNodeModel {
  setAttributes() {
    super.setAttributes()
    this.width = 360
  }
}

export default {
  type: WorkflowNodeType.DocumentSplitNode,
  model: DocumentSplitNodeModel,
  view: DocumentSplitNodeView,
  details: DocumentSplitNodeDetail,
}
