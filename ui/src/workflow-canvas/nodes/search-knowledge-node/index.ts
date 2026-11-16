import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import agent from './agent'
import SearchKnowledgeNodeDetail from './details/index.vue'
import SearchKnowledgeNodeVue from './index.vue'

class SearchKnowledgeNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, SearchKnowledgeNodeVue)
  }
}

export default {
  type: WorkflowNodeType.SearchKnowledge,
  model: WorkflowNodeModel,
  view: SearchKnowledgeNodeView,
  details: SearchKnowledgeNodeDetail,
  agent,
}
