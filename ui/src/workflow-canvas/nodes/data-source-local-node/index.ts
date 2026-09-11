import DataSourceLocalNode from './index.vue'
import DataSourceLocalNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class DataSourceLocalNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, DataSourceLocalNode)
  }
}

export default {
  type: WorkflowNodeType.DataSourceLocalNode,
  model: WorkflowNodeModel,
  view: DataSourceLocalNodeView,
  details: DataSourceLocalNodeDetail,
}
