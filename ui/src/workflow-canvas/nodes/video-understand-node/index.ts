import VideoUnderstandNodeVue from './index.vue'
import VideoUnderstandNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'

class VideoUnderstandNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, VideoUnderstandNodeVue)
  }
}

export default {
  type: WorkflowNodeType.VideoUnderstandNode,
  model: WorkflowNodeModel,
  view: VideoUnderstandNodeView,
  details: VideoUnderstandNodeDetail,
}
