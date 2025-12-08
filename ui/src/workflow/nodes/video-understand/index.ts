import VideoUnderstandNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class VideoUnderstandNode extends AppNode {
  constructor(props: any) {
    super(props, VideoUnderstandNodeVue)
  }
}

export default {
  type: 'video-understand-node',
  model: AppNodeModel,
  view: VideoUnderstandNode
}
