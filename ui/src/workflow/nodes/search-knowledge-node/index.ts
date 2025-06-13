import SearchKnowledgeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class SearchKnowledgeNode extends AppNode {
  constructor(props: any) {
    super(props, SearchKnowledgeVue)
  }
}
export default {
  type: 'search-knowledge-node',
  model: AppNodeModel,
  view: SearchKnowledgeNode
}
