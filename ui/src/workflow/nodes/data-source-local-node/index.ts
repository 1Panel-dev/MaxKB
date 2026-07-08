import DataSourceWebNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class DataSourceWebNode extends AppNode {
  constructor(props: any) {
    super(props, DataSourceWebNodeVue)
  }
}
export default {
  type: 'data-source-local-node',
  model: AppNodeModel,
  view: DataSourceWebNode,
}
