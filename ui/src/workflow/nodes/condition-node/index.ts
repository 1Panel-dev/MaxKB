import ConditioNodeVue from './index.vue'
import { cloneDeep, set } from 'lodash'
import { AppNode, AppNodeModel } from '@/workflow/common/app-node'
class ConditioNode extends AppNode {
  constructor(props: any) {
    super(props, ConditioNodeVue)
  }
}
const get_up_index_height = (condition_list: Array<any>, index: number) => {
  return condition_list
    .filter((item, i) => i < index)
    .map((item) => item.height + 8)
    .reduce((x, y) => x + y, 0)
}
class ConditionModel extends AppNodeModel {
  refreshBranch() {
    // 更新节点连接边的path
    this.incoming.edges.forEach((edge: any) => {
      // 调用自定义的更新方案
      edge.updatePathByAnchor()
    })
    this.outgoing.edges.forEach((edge: any) => {
      edge.updatePathByAnchor()
    })
  }
  getDefaultAnchor() {
    const {
      id,
      x,
      y,
      width,
      height,
      properties: { branch_condition_list }
    } = this
    if (this.height === undefined) {
      this.height = 200
    }
    const anchors: any = []
    anchors.push({
      x: x - width / 2 + 10,
      y: y,
      id: `${id}_left`,
      edgeAddable: false,
      type: 'left'
    })

    if (branch_condition_list) {
      for (let index = 0; index < branch_condition_list.length; index++) {
        const element = branch_condition_list[index]
        const h = get_up_index_height(branch_condition_list, index)
        anchors.push({
          x: x + width / 2 - 10,
          y: y - height / 2 + 75 + h + element.height / 2,
          id: `${id}_${element.id}_right`,
          type: 'right'
        })
      }
    }

    return anchors
  }
}
export default {
  type: 'condition-node',
  model: ConditionModel,
  view: ConditioNode
}
