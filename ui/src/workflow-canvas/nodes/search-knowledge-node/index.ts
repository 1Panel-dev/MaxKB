import SearchKnowledgeNodeVue from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class SearchKnowledgeNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, SearchKnowledgeNodeVue)
  }
}

export default {
  type: WorkflowNodeType.SearchKnowledge,
  model: WorkflowNodeModel,
  view: SearchKnowledgeNodeView,
}
