import DataSourceWebNode from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class DataSourceWebNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, DataSourceWebNode)
  }
}

export default { type: WorkflowNodeType.DataSourceWebNode, model: WorkflowNodeModel, view: DataSourceWebNodeView }
