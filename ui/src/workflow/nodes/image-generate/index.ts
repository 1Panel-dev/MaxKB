import ImageGenerateNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'

class RerankerNode extends AppNode {
  constructor(props: any) {
    super(props, ImageGenerateNodeVue)
  }
}

export default {
  type: 'image-generate-node',
  model: AppNodeModel,
  view: RerankerNode
}
