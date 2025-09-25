import { WorkflowType } from '@/enums/application'
import { t } from '@/locales'

const end_nodes: Array<string> = [
  WorkflowType.AiChat,
  WorkflowType.Reply,
  WorkflowType.ToolLib,
  WorkflowType.ToolLibCustom,
  WorkflowType.ImageUnderstandNode,
  WorkflowType.Application,
  WorkflowType.SpeechToTextNode,
  WorkflowType.TextToSpeechNode,
  WorkflowType.ImageGenerateNode,
  WorkflowType.ImageToVideoGenerateNode,
  WorkflowType.TextToVideoGenerateNode,
  WorkflowType.ImageGenerateNode,
  WorkflowType.LoopBodyNode,
  WorkflowType.LoopNode,
  WorkflowType.LoopBreakNode,
]
export class WorkFlowInstance {
  nodes
  edges
  workFlowNodes: Array<any>
  constructor(workflow: { nodes: Array<any>; edges: Array<any> }) {
    this.nodes = workflow.nodes
    this.edges = workflow.edges
    this.workFlowNodes = []
  }
  /**
   * 校验开始节点
   */
  private is_valid_start_node() {
    const start_node_list = this.nodes.filter((item) =>
      [WorkflowType.Start, WorkflowType.LoopStartNode].includes(item.id),
    )
    if (start_node_list.length == 0) {
      throw t('views.applicationWorkflow.validate.startNodeRequired')
    } else if (start_node_list.length > 1) {
      throw t('views.applicationWorkflow.validate.startNodeOnly')
    }
  }
  /**
   * 校验基本信息节点
   */
  private is_valid_base_node() {
    const start_node_list = this.nodes.filter((item) => item.id === WorkflowType.Base)
    if (start_node_list.length == 0) {
      throw t('views.applicationWorkflow.validate.baseNodeRequired')
    } else if (start_node_list.length > 1) {
      throw t('views.applicationWorkflow.validate.baseNodeOnly')
    }
  }
  /**
   * 校验节点
   */
  is_valid() {
    this.is_valid_start_node()
    this.is_valid_base_node()
    this.is_valid_work_flow()
    this.is_valid_nodes()
  }

  is_loop_valid() {
    this.is_valid_start_node()
    this.is_valid_work_flow()
    this.is_valid_nodes()
  }

  /**
   * 获取开始节点
   * @returns
   */
  get_start_node() {
    const start_node_list = this.nodes.filter((item) =>
      [WorkflowType.Start, WorkflowType.LoopStartNode].includes(item.id),
    )
    return start_node_list[0]
  }
  /**
   * 获取基本节点
   * @returns 基本节点
   */
  get_base_node() {
    const base_node_list = this.nodes.filter((item) => item.id === WorkflowType.Base)
    return base_node_list[0]
  }
  exist_break_node() {
    return this.nodes.some((item) => item.type === WorkflowType.LoopBreakNode)
  }
  /**
   * 校验工作流
   * @param up_node 上一个节点
   */
  private _is_valid_work_flow(up_node?: any) {
    if (!up_node) {
      up_node = this.get_start_node()
    }
    this.workFlowNodes.push(up_node)
    this.is_valid_node(up_node)
    const next_nodes = this.get_next_nodes(up_node)
    for (const next_node of next_nodes) {
      this._is_valid_work_flow(next_node)
    }
  }
  private is_valid_work_flow() {
    this.workFlowNodes = []
    this._is_valid_work_flow()
    const notInWorkFlowNodes = this.nodes
      .filter((node: any) => node.id !== WorkflowType.Start && node.id !== WorkflowType.Base)
      .filter((node) => !this.workFlowNodes.includes(node))
    if (notInWorkFlowNodes.length > 0) {
      throw `${t('views.applicationWorkflow.validate.notInWorkFlowNode')}:${notInWorkFlowNodes.map((node) => node.properties.stepName).join('，')}`
    }
    this.workFlowNodes = []
  }
  /**
   * 获取流程下一个节点列表
   * @param node 节点
   * @returns 节点列表
   */
  private get_next_nodes(node: any) {
    const edge_list = this.edges.filter((edge) => edge.sourceNodeId == node.id)
    const node_list = edge_list
      .map((edge) => this.nodes.filter((node) => node.id == edge.targetNodeId))
      .reduce((x, y) => [...x, ...y], [])
    if (node_list.length == 0 && !end_nodes.includes(node.type)) {
      throw t('views.applicationWorkflow.validate.noNextNode')
    }
    return node_list
  }
  private is_valid_nodes() {
    for (const node of this.nodes) {
      if (
        node.type !== WorkflowType.Base &&
        node.type !== WorkflowType.Start &&
        node.type !== WorkflowType.LoopStartNode
      ) {
        if (!this.edges.some((edge) => edge.targetNodeId === node.id)) {
          throw `${t('views.applicationWorkflow.validate.notInWorkFlowNode')}:${node.properties.stepName}`
        }
      }
    }
  }
  /**
   * 校验节点
   * @param node 节点
   */
  private is_valid_node(node: any) {
    if (node.properties.status && node.properties.status === 500) {
      throw `${node.properties.stepName} ${t('views.applicationWorkflow.validate.nodeUnavailable')}`
    }
    if (node.type === WorkflowType.Condition) {
      const branch_list = node.properties.node_data.branch
      for (const branch of branch_list) {
        const source_anchor_id = `${node.id}_${branch.id}_right`
        const edge_list = this.edges.filter((edge) => edge.sourceAnchorId == source_anchor_id)
        if (edge_list.length == 0) {
          throw `${node.properties.stepName} ${t('views.applicationWorkflow.validate.needConnect1')}${branch.type}${t('views.applicationWorkflow.validate.needConnect2')}`
        }
      }
    } else {
      const edge_list = this.edges.filter((edge) => edge.sourceNodeId == node.id)
      if (edge_list.length == 0 && !end_nodes.includes(node.type)) {
        throw `${node.properties.stepName} ${t('views.applicationWorkflow.validate.cannotEndNode')}`
      }
    }
    if (node.properties.status && node.properties.status !== 200) {
      throw `${node.properties.stepName} ${t('views.applicationWorkflow.validate.nodeUnavailable')}`
    }
  }
}
