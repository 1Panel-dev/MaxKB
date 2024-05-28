import SearchDatasetVue from './index.vue'
import { AppNode, AppNodeModel } from '@/flow/common/app-node/index'
class SearchDatasetNode extends AppNode {
  constructor(props: any) {
    super(props, SearchDatasetVue)
  }
}
export default {
  type: 'search-dataset-node',
  model: AppNodeModel,
  view: SearchDatasetNode
}
