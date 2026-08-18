import type LogicFlow from '@logicflow/core'
import { WorkflowNodeType } from '@/mk-workflow/types'

type WorkflowGraph = {
  edges: LogicFlow.EdgeData[]
  nodes: LogicFlow.NodeData[]
}

/** 校验当前已迁入的智能体工作流节点及其连线关系。 */
export class WorkFlowInstance {
  readonly edges: LogicFlow.EdgeData[]
  readonly nodes: LogicFlow.NodeData[]
  private workflowNodeIds = new Set<string>()

  constructor(workflow: WorkflowGraph) {
    this.nodes = workflow.nodes
    this.edges = workflow.edges
  }

  is_valid_start_node() {
    const startNodes = this.nodes.filter((node) => node.type === WorkflowNodeType.Start)
    if (!startNodes.length) throw new Error('开始节点必填')
    if (startNodes.length > 1) throw new Error('开始节点只能有一个')
  }

  is_valid_base_node() {
    const baseNodes = this.nodes.filter((node) => node.type === WorkflowNodeType.Base)
    if (!baseNodes.length) throw new Error('基本信息节点必填')
    if (baseNodes.length > 1) throw new Error('基本信息节点只能有一个')
  }

  is_valid() {
    this.is_valid_start_node()
    this.is_valid_base_node()
    this.is_valid_work_flow()
    this.is_valid_nodes()
  }

  get_start_node() {
    return this.nodes.find((node) => node.type === WorkflowNodeType.Start)
  }

  get_base_node() {
    return this.nodes.find((node) => node.type === WorkflowNodeType.Base)
  }

  get_next_nodes(node: LogicFlow.NodeData) {
    const targetIds = this.edges
      .filter((edge) => edge.sourceNodeId === node.id)
      .map((edge) => edge.targetNodeId)
    return this.nodes.filter((candidate) => targetIds.includes(candidate.id))
  }

  is_valid_work_flow() {
    const startNode = this.get_start_node()
    if (!startNode) return

    this.workflowNodeIds = new Set<string>()
    const visit = (node: LogicFlow.NodeData) => {
      if (this.workflowNodeIds.has(node.id)) return
      this.workflowNodeIds.add(node.id)
      this.is_valid_node(node)
      this.get_next_nodes(node).forEach(visit)
    }
    visit(startNode)

    const detachedNodes = this.nodes.filter(
      (node) =>
        node.type !== WorkflowNodeType.Base &&
        node.type !== WorkflowNodeType.Start &&
        !this.workflowNodeIds.has(node.id),
    )
    if (detachedNodes.length) {
      throw new Error(
        `未在流程中的节点:${detachedNodes.map((node) => node.properties?.stepName).join('，')}`,
      )
    }
  }

  is_valid_nodes() {
    const detachedNode = this.nodes.find(
      (node) =>
        node.type !== WorkflowNodeType.Base &&
        node.type !== WorkflowNodeType.Start &&
        !this.edges.some((edge) => edge.targetNodeId === node.id),
    )
    if (detachedNode) throw new Error(`未在流程中的节点:${detachedNode.properties?.stepName}`)
  }

  is_valid_node(node: LogicFlow.NodeData) {
    if (node.properties?.status && node.properties.status !== 200) {
      throw new Error(`${node.properties.stepName} 节点不可用`)
    }
    const isTerminalNode = [WorkflowNodeType.AiChat, WorkflowNodeType.Reply].includes(
      node.type as WorkflowNodeType,
    )
    if (!isTerminalNode && !this.edges.some((edge) => edge.sourceNodeId === node.id)) {
      throw new Error(`${node.properties?.stepName} 节点不能当做结束节点`)
    }
  }
}
