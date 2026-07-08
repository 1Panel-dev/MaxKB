import SpeechToTextVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class SpeechToTextNode extends AppNode {
  constructor(props: any) {
    super(props, SpeechToTextVue)
  }
}
export default {
  type: 'speech-to-text-node',
  model: AppNodeModel,
  view: SpeechToTextNode
}
