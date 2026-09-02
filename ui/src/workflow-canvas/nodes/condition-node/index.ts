import ConditionNodeVue from './index.vue'
import { type BaseEdgeModel, type Model } from '@logicflow/core'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'

class ConditionNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, ConditionNodeVue)
  }
}

interface BranchConditionListItem {
  height: number
  id: string
  index: number
}

interface RefreshableEdgeModel extends BaseEdgeModel {
  updatePathByAnchor(): void
}

const getUpIndexHeight = (conditionList: Array<{ height: number }>, index: number) => {
  return conditionList
    .filter((item, i) => i < index)
    .map((item) => item.height + 8)
    .reduce((x, y) => x + y, 0)
}

class ConditionModel extends WorkflowNodeModel {
  refreshBranch() {
    this.incoming.edges.forEach((edge) => {
      ;(edge as RefreshableEdgeModel).updatePathByAnchor()
    })
    this.outgoing.edges.forEach((edge) => {
      ;(edge as RefreshableEdgeModel).updatePathByAnchor()
    })
  }

  override getDefaultAnchor(): Model.AnchorConfig[] {
    const { id, x, y, width, height, properties } = this
    const branchConditionList = (properties as { branch_condition_list?: BranchConditionListItem[] }).branch_condition_list
    const branchList = branchConditionList ?? []
    const currentHeight = height || 200
    const showNode = properties.showNode === undefined ? true : properties.showNode
    const anchors: Model.AnchorConfig[] = []
    anchors.push({
      x: x - width / 2,
      y,
      id: `${id}_left`,
      edgeAddable: false,
      type: 'left',
    })

    for (let index = 0; index < branchList.length; index++) {
      const element = branchList[index]!
      const h = getUpIndexHeight(branchList, index)
      anchors.push({
        x: x + width / 2,
        y: showNode ? y - currentHeight / 2 + 75 + h + element.height / 2 : y,
        id: `${id}_${element.id}_right`,
        type: 'right',
      })
    }

    return anchors
  }
}

export default { type: WorkflowNodeType.Condition, model: ConditionModel, view: ConditionNodeView }
