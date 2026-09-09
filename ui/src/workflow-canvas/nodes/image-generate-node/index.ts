import ImageGenerateNodeVue from './index.vue'
import ImageGenerateNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'

class ImageGenerateNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ImageGenerateNodeVue)
  }
}

export default {
  type: WorkflowNodeType.ImageGenerateNode,
  model: WorkflowNodeModel,
  view: ImageGenerateNodeView,
  details: ImageGenerateNodeDetail,
}
