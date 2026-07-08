import VideoGenerateNodeVue from './index.vue'
import {AppNode, AppNodeModel} from '@/workflow/common/app-node'

class TextToVideoNode extends AppNode {
  constructor(props: any) {
    super(props, VideoGenerateNodeVue)
  }
}

export default {
  type: 'text-to-video-node',
  model: AppNodeModel,
  view: TextToVideoNode
}
