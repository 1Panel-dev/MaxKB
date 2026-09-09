import LoopStartNodeVue from './index.vue'
import LoopStartNodeDetail from './details/index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType, type WorkflowNodeField } from '@/workflow-canvas/types'
import { isLoopBuiltinField, LOOP_BUILTIN_FIELDS } from './constant'

interface LoopStartNodeProperties {
  config?: { fields?: Array<{ label: string; value: string }>; globalFields?: unknown[] }
  loop_input_field_list?: Array<{ field?: string; label?: string; variable?: string }>
  [key: string]: unknown
}

class LoopStartNodeModel extends WorkflowNodeModel {
  override setAttributes() {
    super.setAttributes()
    // 循环引擎内置的 index/item 作为只读输出参数，始终保留在节点自身配置里，保证输出区一定展示
    const config = (this.properties.config ?? {}) as { fields?: unknown[]; globalFields?: unknown[] }
    this.properties.config = {
      ...config,
      fields: LOOP_BUILTIN_FIELDS.map((item) => ({ label: item.label, value: item.field })),
    }
  }

  override getNodeFieldList(): WorkflowNodeField[] {
    const properties = this.properties as LoopStartNodeProperties
    const inputFields = properties.loop_input_field_list
      ? properties.loop_input_field_list
      : (properties.config?.fields ?? []).map((field) => ({ field: field.value, label: field.label, variable: undefined }))
    const loopFields = inputFields
      .map((item) => ({ label: item.label ?? '', value: item.field ?? item.variable ?? '' }))
      .filter((field) => Boolean(field.value) && !isLoopBuiltinField(field.value))
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
  details: LoopStartNodeDetail,
}
