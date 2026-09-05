import ImageToVideoNodeVue from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'

class ImageToVideoNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ImageToVideoNodeVue)
  }
}

export default {
  type: WorkflowNodeType.ImageToVideoGenerateNode,
  model: WorkflowNodeModel,
  view: ImageToVideoNodeView,
}
