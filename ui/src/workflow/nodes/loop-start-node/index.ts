import LoopStartNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
import { t } from '@/locales'
class LoopStartNode extends AppNode {
  constructor(props: any) {
    super(props, LoopStartNodeVue)
  }
  get_node_field_list() {
    const result = []
    if (this.props.model.type === 'loop-start-node') {
      result.push({
        value: 'loop',
        label: t('views.applicationWorkflow.variable.loop'),
        type: 'loop',
        children:
          (this.props.model.properties.loop_input_field_list
            ? this.props.model.properties.loop_input_field_list
            : []
          ).map((i: any) => {
            if (i.label && i.label.input_type === 'TooltipLabel') {
              return { label: i.label.label, value: i.field || i.variable }
            }
            return { label: i.label || i.name, value: i.field || i.variable }
          }) || [],
      })
    }

    result.push({
      value: this.props.model.id,
      label: this.props.model.properties.stepName,
      type: this.props.model.type,
      children: this.props.model.properties?.config?.fields || [],
    })

    return result
  }
}
export default {
  type: 'loop-start-node',
  model: AppNodeModel,
  view: LoopStartNode,
}
