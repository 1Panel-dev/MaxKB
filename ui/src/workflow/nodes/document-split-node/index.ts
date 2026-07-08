import DocumentSplitNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class DocumentSplitNode extends AppNode {
  constructor(props: any) {
    super(props, DocumentSplitNodeVue)
  }
}

export default {
  type: 'document-split-node',
  model: AppNodeModel,
  view: DocumentSplitNode
}
