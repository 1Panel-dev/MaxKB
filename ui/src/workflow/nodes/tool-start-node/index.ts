import ToolBaseNodeVue from './index.vue'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
import { t } from '@/locales'
class ToolBaseNode extends AppNode {
  constructor(props: any) {
    super(props, ToolBaseNodeVue)
  }
  get_node_field_list() {
    const result = []
    result.push({
      value: 'global',
      label: t('workflow.variable.global'),
      type: 'global',
      children: this.props.model.properties?.config?.globalFields || [],
    })
    const tbn = this.props.graphModel.getNodeModelById('tool-base-node')
    console.log(tbn)
    const output = tbn.properties?.user_output_field_list?.map((i: any) => {
      return { label: i.label || i.name, value: i.field }
    })

    result.push({
      value: 'output',
      label: '参数输出',
      type: 'output',
      children: output || [],
    })
    console.log(result)
    return result
  }
}
export default {
  type: 'tool-start-node',
  model: AppNodeModel,
  view: ToolBaseNode,
}
