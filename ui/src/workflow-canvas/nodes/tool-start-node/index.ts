import type { ToolOutputField } from '../tool-base-node/types'
import type { WorkflowNodeField } from '@/workflow-canvas/types'
import type { Model } from '@logicflow/core'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import ToolStartNodeDetail from './details/index.vue'
import ToolStartNode from './index.vue'
import { t } from '@/locales'

class ToolStartNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ToolStartNode)
  }
}

class ToolStartNodeModel extends WorkflowNodeModel {
  getNodeFieldList(): WorkflowNodeField[] {
    const result: WorkflowNodeField[] = []
    result.push({
      value: 'global',
      label: t('workflow.globalVariables.title'),
      type: 'global',
      children: this.properties.config?.globalFields || [],
    })

    const toolBaseNode = this.graphModel.getNodeModelById(WorkflowNodeType.ToolBaseNode)
    const output = ((toolBaseNode?.properties.user_output_field_list ?? []) as ToolOutputField[]).map((field) => ({
      label: field.label || field.name || field.field,
      value: field.field,
    }))

    result.push({
      value: 'output',
      label: t('workflow.toolStart.outputLabel'),
      type: 'output',
      children: output || [],
    })

    return result
  }

  getDefaultAnchor(): Model.AnchorConfig[] {
    const anchors: Model.AnchorConfig[] = []
    anchors.push({ x: this.x + this.width / 2, y: this.y, id: `${this.id}_right`, type: 'right' })
    return anchors
  }
}

export default { type: WorkflowNodeType.ToolStartNode, model: ToolStartNodeModel, view: ToolStartNodeView, details: ToolStartNodeDetail }
