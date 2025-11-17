import KnowledgeWriteVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'


class KnowledgeWriteNode extends AppNode {
    constructor(props: any) {
        super(props, KnowledgeWriteVue)
    }
}

export default {
      type: 'knowledge-write-node',
      model: AppNodeModel,
      view: KnowledgeWriteNode,
}