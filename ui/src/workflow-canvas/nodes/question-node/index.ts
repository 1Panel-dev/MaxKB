import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'
import agent from './agent'
import QuestionNodeDetail from './details/index.vue'
import QuestionNodeVue from './index.vue'

class QuestionNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, QuestionNodeVue)
  }
}

export default {
  type: WorkflowNodeType.Question,
  model: WorkflowNodeModel,
  view: QuestionNodeView,
  details: QuestionNodeDetail,
  agent,
}
