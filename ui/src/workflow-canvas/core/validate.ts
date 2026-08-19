import type LogicFlow from '@logicflow/core'
import { WorkflowNodeType, WorkflowMode, WorkflowKind } from '@/workflow-canvas/types'

interface WorkflowBranch {
  id: string
  type: string
}

interface WorkflowValidationNodeProperties extends LogicFlow.PropertiesType {
  kind?: WorkflowKind
  node_data?: {
    branch?: WorkflowBranch[]
    loop_body?: WorkflowGraphData
  }
  status?: number
  stepName?: string
}

type WorkflowValidationNode = LogicFlow.NodeData & {
  properties: WorkflowValidationNodeProperties
  type: WorkflowNodeType
}

type WorkflowValidationEdge = LogicFlow.EdgeData

interface WorkflowGraphData {
  edges: WorkflowValidationEdge[]
  nodes: WorkflowValidationNode[]
}

const end_nodes: string[] = [
  WorkflowNodeType.AiChat,
  WorkflowNodeType.Reply,
  WorkflowNodeType.ToolLib,
  WorkflowNodeType.ToolLibCustom,
  WorkflowNodeType.ImageUnderstandNode,
  WorkflowNodeType.Application,
  WorkflowNodeType.SpeechToTextNode,
  WorkflowNodeType.TextToSpeechNode,
  WorkflowNodeType.ImageGenerateNode,
  WorkflowNodeType.ImageToVideoGenerateNode,
  WorkflowNodeType.TextToVideoGenerateNode,
  WorkflowNodeType.LoopBodyNode,
  WorkflowNodeType.LoopNode,
  WorkflowNodeType.LoopBreakNode,
  WorkflowNodeType.VideoUnderstandNode,
  WorkflowNodeType.VariableAssignNode,
  WorkflowNodeType.KnowledgeWriteNode,
  WorkflowNodeType.ToolWorkflowLib,
]

const loop_end_nodes: string[] = [
  WorkflowNodeType.AiChat,
  WorkflowNodeType.Reply,
  WorkflowNodeType.ToolLib,
  WorkflowNodeType.ToolLibCustom,
  WorkflowNodeType.ImageUnderstandNode,
  WorkflowNodeType.VideoUnderstandNode,
  WorkflowNodeType.Application,
  WorkflowNodeType.SpeechToTextNode,
  WorkflowNodeType.TextToSpeechNode,
  WorkflowNodeType.ImageGenerateNode,
  WorkflowNodeType.ImageToVideoGenerateNode,
  WorkflowNodeType.TextToVideoGenerateNode,
  WorkflowNodeType.LoopBodyNode,
  WorkflowNodeType.LoopNode,
  WorkflowNodeType.LoopBreakNode,
  WorkflowNodeType.VariableAssignNode,
  WorkflowNodeType.ToolWorkflowLib,
]
const end_nodes_dict: Record<WorkflowMode, string[]> = {
  [WorkflowMode.Application]: end_nodes,
  [WorkflowMode.Knowledge]: [WorkflowNodeType.KnowledgeWriteNode],
  [WorkflowMode.ApplicationLoop]: loop_end_nodes,
  [WorkflowMode.KnowledgeLoop]: [...loop_end_nodes, WorkflowNodeType.KnowledgeWriteNode],
  [WorkflowMode.Tool]: end_nodes,
  [WorkflowMode.ToolLoop]: loop_end_nodes,
}

export class WorkFlowInstance {
  nodes: WorkflowValidationNode[]
  edges: WorkflowValidationEdge[]
  workFlowNodes: WorkflowValidationNode[]
  workflowModel: WorkflowMode

  constructor(workflow: WorkflowGraphData, workflowModel?: WorkflowMode) {
    this.nodes = workflow.nodes
    this.edges = workflow.edges
    this.workFlowNodes = []
    this.workflowModel = workflowModel ? workflowModel : WorkflowMode.Application
  }

  /**
   * 校验开始节点
   */
  is_valid_start_node() {
    const start_node_list = this.nodes.filter(
      (item) => item.id === WorkflowNodeType.Start || item.id === WorkflowNodeType.LoopStartNode,
    )
    if (start_node_list.length == 0) {
      throw '开始节点必填'
    } else if (start_node_list.length > 1) {
      throw '开始节点只能有一个'
    }
  }

  /**
   * 校验基本信息节点
   */
  is_valid_base_node() {
    const start_node_list = this.nodes.filter((item) => item.id === WorkflowNodeType.Base)
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
    const start_node_list = this.nodes.filter(
      (item) =>
        item.id === WorkflowNodeType.Start ||
        item.id === WorkflowNodeType.LoopStartNode ||
        item.id === WorkflowNodeType.ToolStartNode,
    )
    return start_node_list[0]
  }

  /**
   * 获取基本节点
   * @returns 基本节点
   */
  get_base_node() {
    const base_node_list = this.nodes.filter((item) => item.id === WorkflowNodeType.Base)
    return base_node_list[0]
  }

  exist_break_node() {
    return this.nodes.some((item) => item.type === WorkflowNodeType.LoopBreakNode)
  }

  /**
   * 校验工作流
   * @param up_node 上一个节点
   */
  _is_valid_work_flow(up_node?: WorkflowValidationNode) {
    if (!up_node) {
      up_node = this.get_start_node()!
    }
    this.workFlowNodes.push(up_node)
    this.is_valid_node(up_node)
    const next_nodes = this.get_next_nodes(up_node)
    for (const next_node of next_nodes) {
      this._is_valid_work_flow(next_node)
    }
  }

  is_valid_work_flow() {
    this.workFlowNodes = []
    this._is_valid_work_flow()
    const notInWorkFlowNodes = this.nodes
      .filter(
        (node) =>
          node.id !== WorkflowNodeType.Start &&
          node.id !== WorkflowNodeType.Base &&
          node.type !== WorkflowNodeType.ToolBaseNode &&
          node.type !== WorkflowNodeType.ToolStartNode,
      )
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
  get_next_nodes(node: WorkflowValidationNode) {
    const edge_list = this.edges.filter((edge) => edge.sourceNodeId == node.id)
    const node_list = edge_list
      .map((edge) => this.nodes.filter((node) => node.id == edge.targetNodeId))
      .reduce((x, y) => [...x, ...y], [])
    const end = end_nodes_dict[this.workflowModel]
    if (node_list.length == 0 && !end.includes(node.type)) {
      throw '不存在的下一个节点'
    }
    return node_list
  }

  is_valid_nodes() {
    for (const node of this.nodes) {
      if (
        node.type !== WorkflowNodeType.Base &&
        node.type !== WorkflowNodeType.Start &&
        node.type !== WorkflowNodeType.LoopStartNode &&
        node.type !== WorkflowNodeType.ToolBaseNode &&
        node.type !== WorkflowNodeType.ToolStartNode
      ) {
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
  is_valid_node(node: WorkflowValidationNode) {
    if (node.properties.status && node.properties.status === 500) {
      throw `${node.properties.stepName} 节点不可用`
    }
    if (node.type === WorkflowNodeType.Condition) {
      const branch_list = node.properties.node_data!.branch!
      for (const branch of branch_list) {
        const source_anchor_id = `${node.id}_${branch.id}_right`
        const edge_list = this.edges.filter((edge) => edge.sourceAnchorId == source_anchor_id)
        if (edge_list.length == 0) {
          throw `${node.properties.stepName} 节点的${branch.type}分支需要连接`
        }
      }
    } else {
      const edge_list = this.edges.filter((edge) => edge.sourceNodeId == node.id)
      const end = end_nodes_dict[this.workflowModel]
      if (edge_list.length == 0 && !end.includes(node.type)) {
        throw `${node.properties.stepName} 节点不能当做结束节点`
      }
    }
    if (node.properties.status && node.properties.status !== 200) {
      throw `${node.properties.stepName} 节点不可用`
    }
  }
}
export class ToolWorkFlowInstance extends WorkFlowInstance {
  is_valid_start_node() {
    const start_node_list = this.nodes.filter(
      (item) => item.type === WorkflowNodeType.ToolStartNode,
    )

    if (start_node_list.length == 0) {
      throw '开始节点必填'
    }
  }
  /**
   * 校验基本信息节点
   */
  is_valid_base_node() {
    const base_node_list = this.nodes.filter((item) => item.id === WorkflowNodeType.ToolBaseNode)
    if (base_node_list.length == 0) {
      throw '基本信息节点必填'
    } else if (base_node_list.length > 1) {
      throw '基本信息节点只能有一个'
    }
  }
  get_start_nodes() {
    return this.nodes.filter((item) => item.type === WorkflowNodeType.ToolStartNode)
  }
  get_base_node() {
    const base_node_list = this.nodes.filter((item) => item.id === WorkflowNodeType.ToolBaseNode)
    return base_node_list[0]
  }
}
export class KnowledgeWorkFlowInstance extends WorkFlowInstance {
  is_valid_start_node() {
    const start_node_list =
      this.workflowModel == WorkflowMode.Knowledge
        ? this.nodes.filter((item) => item.properties.kind === WorkflowKind.DataSource)
        : this.nodes.filter((item) => item.type === WorkflowNodeType.LoopStartNode)

    if (start_node_list.length == 0) {
      throw '开始节点必填'
    }
  }
  /**
   * 校验基本信息节点
   */
  is_valid_base_node() {
    const base_node_list = this.nodes.filter((item) => item.id === WorkflowNodeType.KnowledgeBase)
    if (base_node_list.length == 0) {
      throw '基本信息节点必填'
    } else if (base_node_list.length > 1) {
      throw '基本信息节点只能有一个'
    }
  }

  is_valid_work_flow() {
    this.workFlowNodes = []
    const start_node_list = this.get_start_nodes()
    start_node_list.forEach((n) => {
      this._is_valid_work_flow(n)
    })

    const notInWorkFlowNodes = this.nodes
      .filter(
        (node) =>
          node.id !== WorkflowNodeType.KnowledgeBase &&
          node.type !== WorkflowNodeType.LoopStartNode &&
          node.properties.kind !== WorkflowKind.DataSource,
      )
      .filter((node) => !this.workFlowNodes.includes(node))
    if (notInWorkFlowNodes.length > 0) {
      throw `未在流程中的节点:${notInWorkFlowNodes.map((node) => node.properties.stepName).join('，')}`
    }
    this.workFlowNodes = []
  }

  is_valid_nodes() {
    for (const node of this.nodes) {
      if (
        node.type !== WorkflowNodeType.KnowledgeBase &&
        node.type !== WorkflowNodeType.LoopStartNode &&
        node.properties.kind !== WorkflowKind.DataSource
      ) {
        if (!this.edges.some((edge) => edge.targetNodeId === node.id)) {
          throw `未在流程中的节点:${node.properties.stepName}`
        }
      }
    }
  }
  get_start_nodes() {
    if (this.workflowModel == WorkflowMode.Knowledge) {
      return this.nodes.filter((item) => item.properties.kind === WorkflowKind.DataSource)
    } else {
      return this.nodes.filter((item) => item.type === WorkflowNodeType.LoopStartNode)
    }
  }
  get_end_nodes() {
    const start_node_list = this.get_start_nodes()
    return start_node_list.flatMap((n) => {
      return this._get_end_nodes(n, [])
    })
  }
  _get_end_nodes(startNode: WorkflowValidationNode, value: WorkflowValidationNode[]) {
    const next = this.get_next_nodes(startNode)
    if (next.length == 0) {
      value.push(startNode)
    } else {
      next.forEach((n) => {
        this._get_end_nodes(n, value)
      })
    }
    return value
  }

  /**
   * 获取流程下一个节点列表
   * @param node 节点
   * @returns 节点列表
   */
  get_next_nodes(node: WorkflowValidationNode) {
    const edge_list = this.edges.filter((edge) => edge.sourceNodeId == node.id)
    const node_list = edge_list
      .map((edge) => this.nodes.filter((node) => node.id == edge.targetNodeId))
      .reduce((x, y) => [...x, ...y], [])

    return node_list
  }

  /**
   * 校验节点
   * @param node 节点
   */
  is_valid_node(node: WorkflowValidationNode) {
    if (node.properties.status && node.properties.status === 500) {
      throw `${node.properties.stepName} 节点不可用`
    }
    if (node.type === WorkflowNodeType.Condition) {
      const branch_list = node.properties.node_data!.branch!
      for (const branch of branch_list) {
        const source_anchor_id = `${node.id}_${branch.id}_right`
        const edge_list = this.edges.filter((edge) => edge.sourceAnchorId == source_anchor_id)
        if (edge_list.length == 0) {
          throw `${node.properties.stepName} 节点的${branch.type}分支需要连接`
        }
      }
    } else {
      const edge_list = this.edges.filter((edge) => edge.sourceNodeId == node.id)
      const end = end_nodes_dict[this.workflowModel]
      if (this.workflowModel == WorkflowMode.KnowledgeLoop) {
        if (edge_list.length == 0 && !end.includes(node.type)) {
          throw `${node.properties.stepName} 节点不能当做结束节点`
        }
        return
      }
      if (edge_list.length == 0 && !end.includes(node.type)) {
        if (node.type == WorkflowNodeType.LoopNode) {
          const loopBody = node.properties.node_data?.loop_body
          if (loopBody) {
            const end_nodes = new KnowledgeWorkFlowInstance(
              loopBody,
              WorkflowMode.KnowledgeLoop,
            ).get_end_nodes()
            if (!end_nodes.every((n) => end.includes(n.type))) {
              throw `${node.properties.stepName} 节点不能当做结束节点`
            }
          }
        } else {
          throw `${node.properties.stepName} 节点不能当做结束节点`
        }
      }
    }
    if (node.properties.status && node.properties.status !== 200) {
      throw `${node.properties.stepName} 节点不可用`
    }
  }
}
