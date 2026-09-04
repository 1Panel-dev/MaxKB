import ToolStartNode from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType, type WorkflowNodeField } from '@/workflow-canvas/types.ts'
import type { Model } from '@logicflow/core'

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
      label: '全局变量',
      type: 'global',
      children: this.properties.config?.globalFields || [],
    })

    const toolBaseNode = this.graphModel.getNodeModelById(WorkflowNodeType.ToolBaseNode)
    const output = (toolBaseNode?.properties?.user_output_field_list as any[])?.map((i: any) => {
      return { label: i.label || i.name, value: i.field }
    })

    result.push({
      value: 'output',
      label: '参数输出',
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

export default { type: WorkflowNodeType.ToolStartNode, model: ToolStartNodeModel, view: ToolStartNodeView }