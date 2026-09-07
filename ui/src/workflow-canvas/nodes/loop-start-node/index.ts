import LoopStartNodeVue from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType, type WorkflowNodeField } from '@/workflow-canvas/types'

interface LoopStartNodeProperties {
  config?: { fields?: Array<{ label: string; value: string }>; globalFields?: unknown[] }
  loop_input_field_list?: Array<{ field?: string; label?: string; variable?: string }>
  [key: string]: unknown
}

class LoopStartNodeModel extends WorkflowNodeModel {
  override getNodeFieldList(): WorkflowNodeField[] {
    const properties = this.properties as LoopStartNodeProperties
    const inputFields =
      properties.loop_input_field_list && properties.loop_input_field_list.length
        ? properties.loop_input_field_list.map((item) => ({ field: item.field ?? item.variable ?? '', label: item.label ?? '' }))
        : (properties.config?.fields ?? []).map((field) => ({ field: field.value, label: field.label }))
    const loopFields = inputFields.map((item) => ({ label: item.label, value: item.field })).filter((field) => Boolean(field.value))
    return [{ value: 'loop', label: '循环变量', type: 'loop', children: loopFields }, ...super.getNodeFieldList()]
  }
}

class LoopStartNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, LoopStartNodeVue)
  }
}

export default {
  type: WorkflowNodeType.LoopStartNode,
  model: LoopStartNodeModel,
  view: LoopStartNodeView,
}
