import { WorkflowType } from '@/enums/workflow'

const end_nodes = [WorkflowType.AiChat, WorkflowType.Reply]
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
    const start_node_list = this.nodes.filter((item) => item.id === WorkflowType.Start)
    if (start_node_list.length == 0) {
      throw '开始节点必填'
    } else if (start_node_list.length > 1) {
      throw '开始节点只能有一个'
    }
  }
  /**
   * 校验基本信息节点
   */
  private is_valid_base_node() {
    const start_node_list = this.nodes.filter((item) => item.id === WorkflowType.Base)
    if (start_node_list.length == 0) {
      throw '基本信息节点必填'
    } else if (start_node_list.length > 1) {
      throw '基本信息节点只能有一个'
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

  /**
   * 获取开始节点
   * @returns
   */
  get_start_node() {
    const start_node_list = this.nodes.filter((item) => item.id === WorkflowType.Start)
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
      throw `未在流程中的节点:${notInWorkFlowNodes.map((node) => node.properties.stepName).join('，')}`
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
      throw '不存在的下一个节点'
    }
    return node_list
  }
  private is_valid_nodes() {
    for (const node of this.nodes) {
      if (node.type !== WorkflowType.Base && node.type !== WorkflowType.Start) {
        if (!this.edges.some((edge) => edge.targetNodeId === node.id)) {
          throw `未在流程中的节点:${node.properties.stepName}`
        }
      }
    }
  }
  /**
   * 校验节点
   * @param node 节点
   */
  private is_valid_node(node: any) {
    if (node.type === WorkflowType.Condition) {
      const branch_list = node.properties.node_data.branch
      for (const branch of branch_list) {
        const source_anchor_id = `${node.id}_${branch.id}_right`
        const edge_list = this.edges.filter((edge) => edge.sourceAnchorId == source_anchor_id)
        if (edge_list.length == 0) {
          throw `${node.properties.stepName} 节点的${branch.type}分支需要连接`
        } else if (edge_list.length > 1) {
          throw `${node.properties.stepName} 节点的${branch.type}分支不能连接俩个节点`
        }
      }
    } else {
      const edge_list = this.edges.filter((edge) => edge.sourceNodeId == node.id)
      if (edge_list.length == 0 && !end_nodes.includes(node.type)) {
        throw `${node.properties.stepName} 节点不能当做结束节点`
      } else if (edge_list.length > 1) {
        throw `${node.properties.stepName} 节点不能连接俩个节点`
      }
    }
  }
}
