import FormNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class FormNode extends AppNode {
  constructor(props: any) {
    super(props, FormNodeVue)
  }
  get_node_field_list() {
    const result = []
    const fields = this.props.model.properties?.config?.fields || []

    try {
      this.props.model.properties.node_data.form_field_list.forEach((item: any) => {
        if (!fields.some((f: any) => f.value === item.field)) {
          fields.push({
            value: item.field,
            label: typeof item.label == 'string' ? item.label : item.label.label
          })
        }
      })
    } catch (e) {}
    result.push({
      value: this.props.model.id,
      label: this.props.model.properties.stepName,
      type: this.props.model.type,
      children: fields
    })
    return result
  }
}
export default {
  type: 'form-node',
  model: AppNodeModel,
  view: FormNode
}
