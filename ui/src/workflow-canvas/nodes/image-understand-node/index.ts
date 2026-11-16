import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'
import agent from './agent'
import ImageUnderstandNodeDetail from './details/index.vue'
import ImageUnderstandNodeVue from './index.vue'

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
  agent,
}
