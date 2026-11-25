import type { WorkflowNodeField } from '@/workflow-canvas/types'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import KnowledgeBaseNode from './index.vue'
import { t } from '@/locales'

class KnowledgeBaseNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, KnowledgeBaseNode)
  }
}

class KnowledgeBaseNodeModel extends WorkflowNodeModel {
  setAttributes() {
    super.setAttributes()
    this.width = 600
  }

  getNodeFieldList(): WorkflowNodeField[] {
    return [
      {
        value: 'global',
        label: t('workflow.globalVariables.title'),
        type: 'global',
        children: this.properties.config?.globalFields ?? [],
      },
      ...super.getNodeFieldList(),
    ]
  }
}

export default { type: WorkflowNodeType.KnowledgeBase, model: KnowledgeBaseNodeModel, view: KnowledgeBaseNodeView }
