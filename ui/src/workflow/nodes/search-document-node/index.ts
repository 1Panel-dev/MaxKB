import SearchDocumentVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class SearchDocumentNode extends AppNode {
  constructor(props: any) {
    super(props, SearchDocumentVue)
  }
}

export default {
  type: 'search-document-node',
  model: AppNodeModel,
  view: SearchDocumentNode
}
