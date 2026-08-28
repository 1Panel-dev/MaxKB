import { WorkflowKind } from './../../enums/application'
import { WorkflowType, WorkflowMode } from '@/enums/application'

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
  WorkflowType.LoopBodyNode,
  WorkflowType.LoopNode,
  WorkflowType.LoopBreakNode,
  WorkflowType.VideoUnderstandNode,
  WorkflowType.VariableAssignNode,
  WorkflowType.KnowledgeWriteNode,
  WorkflowType.ToolWorkflowLib,
]

const loop_end_nodes: Array<string> = [
  WorkflowType.AiChat,
  WorkflowType.Reply,
  WorkflowType.ToolLib,
  WorkflowType.ToolLibCustom,
  WorkflowType.ImageUnderstandNode,
  WorkflowType.VideoUnderstandNode,
  WorkflowType.Application,
  WorkflowType.SpeechToTextNode,
  WorkflowType.TextToSpeechNode,
  WorkflowType.ImageGenerateNode,
  WorkflowType.ImageToVideoGenerateNode,
  WorkflowType.TextToVideoGenerateNode,
  WorkflowType.LoopBodyNode,
  WorkflowType.LoopNode,
  WorkflowType.LoopBreakNode,
  WorkflowType.VariableAssignNode,
  WorkflowType.ToolWorkflowLib,
]
const end_nodes_dict = {
  [WorkflowMode.Application]: end_nodes,
  [WorkflowMode.Knowledge]: [WorkflowType.KnowledgeWriteNode],
  [WorkflowMode.ApplicationLoop]: loop_end_nodes,
  [WorkflowMode.KnowledgeLoop]: [...loop_end_nodes, WorkflowType.KnowledgeWriteNode],
  [WorkflowMode.Tool]: end_nodes,
  [WorkflowMode.ToolLoop]: loop_end_nodes,
}

export class WorkFlowInstance {
  nodes
  edges
  workFlowNodes: Array<any>
  workflowModel: WorkflowMode

  constructor(workflow: { nodes: Array<any>; edges: Array<any> }, workflowModel?: WorkflowMode) {
    this.nodes = workflow.nodes
    this.edges = workflow.edges
    this.workFlowNodes = []
    this.workflowModel = workflowModel ? workflowModel : WorkflowMode.Application
  }

  /**
   * 校验开始节点
   */
  is_valid_start_node() {
    const start_node_list = this.nodes.filter((item) =>
      [WorkflowType.Start, WorkflowType.LoopStartNode].includes(item.id),
    )
    if (start_node_list.length == 0) {
      throw t('workflow.validate.startNodeRequired')
    } else if (start_node_list.length > 1) {
      throw t('workflow.validate.startNodeOnly')
    }
  }

  /**
   * 校验基本信息节点
   */
  is_valid_base_node() {
    const start_node_list = this.nodes.filter((item) => item.id === WorkflowType.Base)
    if (start_node_list.length == 0) {
      throw t('workflow.validate.baseNodeRequired')
    } else if (start_node_list.length > 1) {
      throw t('workflow.validate.baseNodeOnly')
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
      [WorkflowType.Start, WorkflowType.LoopStartNode, WorkflowType.ToolStartNode].includes(
        item.id,
      ),
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
  _is_valid_work_flow(up_node?: any) {
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

  is_valid_work_flow() {
    this.workFlowNodes = []
    this._is_valid_work_flow()
    const notInWorkFlowNodes = this.nodes
      .filter(
        (node: any) =>
          node.id !== WorkflowType.Start &&
          node.id !== WorkflowType.Base &&
          node.type !== WorkflowType.ToolBaseNode &&
          node.type !== WorkflowType.ToolStartNode,
      )
      .filter((node) => !this.workFlowNodes.includes(node))
    if (notInWorkFlowNodes.length > 0) {
      throw `${t('workflow.validate.notInWorkFlowNode')}:${notInWorkFlowNodes.map((node) => node.properties.stepName).join('，')}`
    }
    this.workFlowNodes = []
  }

  /**
   * 获取流程下一个节点列表
   * @param node 节点
   * @returns 节点列表
   */
  get_next_nodes(node: any) {
    const edge_list = this.edges.filter((edge) => edge.sourceNodeId == node.id)
    const node_list = edge_list
      .map((edge) => this.nodes.filter((node) => node.id == edge.targetNodeId))
      .reduce((x, y) => [...x, ...y], [])
    const end = end_nodes_dict[this.workflowModel]
    if (node_list.length == 0 && !end.includes(node.type)) {
      throw t('workflow.validate.noNextNode')
    }
    return node_list
  }

  is_valid_nodes() {
    for (const node of this.nodes) {
      if (
        node.type !== WorkflowType.Base &&
        node.type !== WorkflowType.Start &&
        node.type !== WorkflowType.LoopStartNode &&
        node.type !== WorkflowType.ToolBaseNode &&
        node.type !== WorkflowType.ToolStartNode
      ) {
        if (!this.edges.some((edge) => edge.targetNodeId === node.id)) {
          throw `${t('workflow.validate.notInWorkFlowNode')}:${node.properties.stepName}`
        }
      }
    }
  }

  /**
   * 校验节点
   * @param node 节点
   */
  is_valid_node(node: any) {
    if (node.properties.status && node.properties.status === 500) {
      throw `${node.properties.stepName} ${t('workflow.validate.nodeUnavailable')}`
    }
    if (node.type === WorkflowType.Condition) {
      const branch_list = node.properties.node_data.branch
      for (const branch of branch_list) {
        const source_anchor_id = `${node.id}_${branch.id}_right`
        const edge_list = this.edges.filter((edge) => edge.sourceAnchorId == source_anchor_id)
        if (edge_list.length == 0) {
          throw `${node.properties.stepName} ${t('workflow.validate.needConnect1')}${branch.type}${t('workflow.validate.needConnect2')}`
        }
      }
    } else {
      const edge_list = this.edges.filter((edge) => edge.sourceNodeId == node.id)
      const end = end_nodes_dict[this.workflowModel]
      if (edge_list.length == 0 && !end.includes(node.type)) {
        throw `${node.properties.stepName} ${t('workflow.validate.cannotEndNode')}`
      }
    }
    if (node.properties.status && node.properties.status !== 200) {
      throw `${node.properties.stepName} ${t('workflow.validate.nodeUnavailable')}`
    }
  }
}
export class ToolWorkFlowInstance extends WorkFlowInstance {
  is_valid_start_node() {
    const start_node_list = this.nodes.filter((item) => item.type === WorkflowType.ToolStartNode)

    if (start_node_list.length == 0) {
      throw t('workflow.validate.startNodeRequired')
    }
  }
  /**
   * 校验基本信息节点
   */
  is_valid_base_node() {
    const base_node_list = this.nodes.filter((item) => item.id === WorkflowType.ToolBaseNode)
    if (base_node_list.length == 0) {
      throw t('workflow.validate.baseNodeRequired')
    } else if (base_node_list.length > 1) {
      throw t('workflow.validate.baseNodeOnly')
    }
  }
  get_start_nodes() {
    return this.nodes.filter((item) => item.type === WorkflowType.ToolStartNode)
  }
  get_base_node() {
    const base_node_list = this.nodes.filter((item) => item.id === WorkflowType.ToolBaseNode)
    return base_node_list[0]
  }
}
export class KnowledgeWorkFlowInstance extends WorkFlowInstance {
  is_valid_start_node() {
    const start_node_list =
      this.workflowModel == WorkflowMode.Knowledge
        ? this.nodes.filter((item) => item.properties.kind === WorkflowKind.DataSource)
        : this.nodes.filter((item) => item.type === WorkflowType.LoopStartNode)

    if (start_node_list.length == 0) {
      throw t('workflow.validate.startNodeRequired')
    }
  }
  /**
   * 校验基本信息节点
   */
  is_valid_base_node() {
    const base_node_list = this.nodes.filter((item) => item.id === WorkflowType.KnowledgeBase)
    if (base_node_list.length == 0) {
      throw t('workflow.validate.baseNodeRequired')
    } else if (base_node_list.length > 1) {
      throw t('workflow.validate.baseNodeOnly')
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
        (node: any) =>
          node.id !== WorkflowType.KnowledgeBase &&
          node.type !== WorkflowType.LoopStartNode &&
          node.properties.kind !== WorkflowKind.DataSource,
      )
      .filter((node) => !this.workFlowNodes.includes(node))
    if (notInWorkFlowNodes.length > 0) {
      throw `${t('workflow.validate.notInWorkFlowNode')}:${notInWorkFlowNodes.map((node) => node.properties.stepName).join('，')}`
    }
    this.workFlowNodes = []
  }

  is_valid_nodes() {
    for (const node of this.nodes) {
      if (
        node.type !== WorkflowType.KnowledgeBase &&
        node.type !== WorkflowType.LoopStartNode &&
        node.properties.kind !== WorkflowKind.DataSource
      ) {
        if (!this.edges.some((edge) => edge.targetNodeId === node.id)) {
          throw `${t('workflow.validate.notInWorkFlowNode')}:${node.properties.stepName}`
        }
      }
    }
  }
  get_start_nodes() {
    if (this.workflowModel == WorkflowMode.Knowledge) {
      return this.nodes.filter((item) => item.properties.kind === WorkflowKind.DataSource)
    } else {
      return this.nodes.filter((item) => item.type === WorkflowType.LoopStartNode)
    }
  }
  get_end_nodes() {
    const start_node_list = this.get_start_nodes()
    return start_node_list.flatMap((n) => {
      return this._get_end_nodes(n, [])
    })
  }
  _get_end_nodes(startNode: any, value: Array<any>) {
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
  get_next_nodes(node: any) {
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
  is_valid_node(node: any) {
    if (node.properties.status && node.properties.status === 500) {
      throw `${node.properties.stepName} ${t('workflow.validate.nodeUnavailable')}`
    }
    if (node.type === WorkflowType.Condition) {
      const branch_list = node.properties.node_data.branch
      for (const branch of branch_list) {
        const source_anchor_id = `${node.id}_${branch.id}_right`
        const edge_list = this.edges.filter((edge) => edge.sourceAnchorId == source_anchor_id)
        if (edge_list.length == 0) {
          throw `${node.properties.stepName} ${t('workflow.validate.needConnect1')}${branch.type}${t('workflow.validate.needConnect2')}`
        }
      }
    } else {
      const edge_list = this.edges.filter((edge) => edge.sourceNodeId == node.id)
      const end = end_nodes_dict[this.workflowModel]
      if (this.workflowModel == WorkflowMode.KnowledgeLoop) {
        if (edge_list.length == 0 && !end.includes(node.type)) {
          throw `${node.properties.stepName} ${t('workflow.validate.cannotEndNode')}`
        }
        return
      }
      if (edge_list.length == 0 && !end.includes(node.type)) {
        if (node.type == WorkflowType.LoopNode) {
          if (node.properties.node_data.loop_body) {
            const end_nodes = new KnowledgeWorkFlowInstance(
              node.properties.node_data.loop_body,
              WorkflowMode.KnowledgeLoop,
            ).get_end_nodes()
            if (!end_nodes.every((n) => end.includes(n.type))) {
              throw `${node.properties.stepName} ${t('workflow.validate.cannotEndNode')}`
            }
          }
        } else {
          throw `${node.properties.stepName} ${t('workflow.validate.cannotEndNode')}`
        }
      }
    }
    if (node.properties.status && node.properties.status !== 200) {
      throw `${node.properties.stepName} ${t('workflow.validate.nodeUnavailable')}`
    }
  }
}

// 节点类型 -> 默认模型类别(与后端 NODE_DEFAULT_MODEL_TYPE 保持一致)
const NODE_DEFAULT_MODEL_TYPE: Record<string, string> = {
  'ai-chat-node': 'LLM',
  'question-node': 'LLM',
  'intent-node': 'LLM',
  'parameter-extraction-node': 'LLM',
  'image-understand-node': 'IMAGE',
  'video-understand-node': 'IMAGE',
  'image-generate-node': 'TTI',
  'text-to-video-node': 'TTV',
  'image-to-video-node': 'ITV',
  'speech-to-text-node': 'STT',
  'text-to-speech-node': 'TTS',
  'reranker-node': 'RERANKER',
}

/**
 * 与后端 validate_workflow_default_models 对齐:
 * 节点选择「默认模型」但对应类别默认模型未配置时,发布前拦截。
 * 抛出 { node, errMessage },由发布流程外层 catch 展示,与「自定义模型为空」等节点校验一致。
 */
export function validateWorkflowDefaultModels(work_flow: any, default_model_setting: any) {
  const setting = default_model_setting || {}
  const hasModel = (type: string) => !!((setting[type] || {}) as any).model_id
  const errMessage = t('workflow.setting.defaultModelRequired')

  const walk = (nodes: any[]) => {
    for (const node of nodes || []) {
      const nd = node?.properties?.node_data || {}
      const nodeType = node?.type
      if (nodeType === 'base-node') {
        // base-node 只有 default/custom(tts 另有 BROWSER)
        if (nd.stt_model_enable && nd.stt_model_id_type === 'default' && !hasModel('STT')) {
          throw { node, errMessage }
        }
        if (nd.tts_model_enable && nd.tts_type === 'DEFAULT' && !hasModel('TTS')) {
          throw { node, errMessage }
        }
        if (nd.long_term_enable && nd.long_term_model_id_type === 'default' && !hasModel('LLM')) {
          throw { node, errMessage }
        }
        continue
      }
      const modelType = NODE_DEFAULT_MODEL_TYPE[nodeType]
      if (modelType) {
        const typeKey =
          nodeType === 'reranker-node'
            ? 'reranker_model_id_type'
            : nodeType === 'speech-to-text-node'
              ? 'stt_model_id_type'
              : nodeType === 'text-to-speech-node'
                ? 'tts_model_id_type'
                : 'model_id_type'
        if ((nd[typeKey] || 'custom') === 'default' && !hasModel(modelType)) {
          throw { node, errMessage }
        }
      }
      if (nodeType === 'loop-node' && nd.loop_body?.nodes) {
        walk(nd.loop_body.nodes)
      }
    }
  }
  walk(work_flow?.nodes)
}
