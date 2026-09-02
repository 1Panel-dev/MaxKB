import QuestionNodeVue from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types.ts'

class QuestionNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, QuestionNodeVue)
  }
}

export default {
  type: WorkflowNodeType.Question,
  model: WorkflowNodeModel,
  view: QuestionNodeView,
}
