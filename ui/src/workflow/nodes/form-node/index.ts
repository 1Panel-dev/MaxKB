import FormNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class FormNode extends AppNode {
  constructor(props: any) {
    super(props, FormNodeVue)
  }
  get_node_field_list() {
    const result = []
    const fields = this.props.model.properties?.config?.fields || []
    let otherFields = []
    try {
      otherFields = this.props.model.properties.node_data.form_field_list.map((item: any) => ({
        label: typeof item.label == 'string' ? item.label : item.label.label,
        value: item.field
      }))
    } catch (e) {}
    result.push({
      value: this.props.model.id,
      label: this.props.model.properties.stepName,
      type: this.props.model.type,
      children: [...fields, ...otherFields]
    })
    return result
  }
}
export default {
  type: 'form-node',
  model: AppNodeModel,
  view: FormNode
}
