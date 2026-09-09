import ImageUnderstandNodeVue from './index.vue'
import ImageUnderstandNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'

class ImageUnderstandNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ImageUnderstandNodeVue)
  }
}

export default {
  type: WorkflowNodeType.ImageUnderstandNode,
  model: WorkflowNodeModel,
  view: ImageUnderstandNodeView,
  details: ImageUnderstandNodeDetail,
}
