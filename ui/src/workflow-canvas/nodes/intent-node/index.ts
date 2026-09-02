import IntentNodeViewVue from './index.vue'
import { WorkflowNodeModel, WorkflowNodeView } from '@/workflow-canvas/core/workflow-node'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import { randomId } from '@/utils/common'
import type { Model } from '@logicflow/core'

interface IntentNodeBranch {
  id: string
  content: string
  isOther: boolean
}

interface IntentNodeData {
  model_id: string
  model_id_type: 'custom' | 'reference'
  model_id_reference: string[]
  model_params_setting: Record<string, unknown>
  content_list: string[]
  dialogue_type: 'NODE' | 'WORKFLOW'
  dialogue_number: number
  branch: IntentNodeBranch[]
}

/** 节点顶部到第一个分类行锚点的纵向偏移（近似）。 */
const BRANCH_ANCHOR_TOP_OFFSET = 400
/** 相邻分类行锚点的纵向间距（近似行高）。 */
const BRANCH_ANCHOR_GAP = 40

type UpdatePathEdge = { updatePathByAnchor: () => void }

function defaultBranch(): IntentNodeBranch[] {
  return [
    { id: randomId(), content: '', isOther: false },
    { id: randomId(), content: '其他', isOther: true },
  ]
}

function defaultNodeData(): IntentNodeData {
  return {
    model_id: '',
    model_id_type: 'custom',
    model_id_reference: [],
    model_params_setting: {},
    content_list: [],
    dialogue_type: 'WORKFLOW',
    dialogue_number: 1,
    branch: defaultBranch(),
  }
}

class IntentNodeModel extends WorkflowNodeModel {
  setAttributes() {
    super.setAttributes()
    // 预置 node_data 为一个可用的默认分支，保证 Vue 表单挂载前锚点已存在
    const nodeData = this.properties.node_data as IntentNodeData | undefined
    if (!nodeData) {
      this.properties.node_data = defaultNodeData()
    } else if (!Array.isArray(nodeData.branch) || nodeData.branch.length === 0) {
      nodeData.branch = defaultBranch()
    }
  }

  refreshBranch() {
    this.incoming.edges.forEach((edge) => (edge as unknown as UpdatePathEdge).updatePathByAnchor())
    this.outgoing.edges.forEach((edge) => (edge as unknown as UpdatePathEdge).updatePathByAnchor())
  }

  getDefaultAnchor(): Model.AnchorConfig[] {
    const { id, x, y, width, height } = this
    const anchors: Model.AnchorConfig[] = []

    anchors.push({
      x: x - width / 2,
      y,
      id: `${id}_left`,
      type: 'left',
      edgeAddable: false,
    })

    const showNode = this.properties.showNode ?? true
    const nodeData = this.properties.node_data as IntentNodeData | undefined
    const branchList = Array.isArray(nodeData?.branch) ? nodeData.branch : []

    if (!showNode) {
      // 收起后所有分支锚点归并为“其他”一个右锚点，节点只显示一个右锚点。
      const mergeTarget =
        branchList.find((branch) => branch.isOther) ?? branchList[branchList.length - 1]
      if (mergeTarget) {
        anchors.push({
          x: x + width / 2,
          y,
          id: `${id}_${mergeTarget.id}_right`,
          type: 'right',
        })
      }
      return anchors
    }

    // 展开时每个分支一个右锚点，锚点从节点顶部偏移近似对齐到各分类行，
    // 锚点 id 由后端 branch_anchor(branch_id) 约定为 `${id}_${branch_id}_right`。
    const startY = y - height / 2 + BRANCH_ANCHOR_TOP_OFFSET
    branchList.forEach((branch, index) => {
      anchors.push({
        x: x + width / 2,
        y: startY + index * BRANCH_ANCHOR_GAP,
        id: `${id}_${branch.id}_right`,
        type: 'right',
      })
    })

    return anchors
  }
}

class IntentNodeView extends WorkflowNodeView {
  constructor(props: ConstructorParameters<typeof WorkflowNodeView>[0]) {
    super(props, IntentNodeViewVue)
  }
}

export default {
  type: WorkflowNodeType.IntentNode,
  model: IntentNodeModel,
  view: IntentNodeView,
}
