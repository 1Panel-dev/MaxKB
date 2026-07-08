import TextToSpeechVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class TextToSpeechNode extends AppNode {
  constructor(props: any) {
    super(props, TextToSpeechVue)
  }
}
export default {
  type: 'text-to-speech-node',
  model: AppNodeModel,
  view: TextToSpeechNode
}
