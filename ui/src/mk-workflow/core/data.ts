import type LogicFlow from '@logicflow/core'
import { WorkflowNodeType, WorkflowMode } from '@/mk-workflow/types'

export interface WorkflowField {
  label: string
  value: string
}

export interface WorkflowNodeDefinition {
  height: number
  label: string
  properties: LogicFlow.PropertiesType
  text: string
  type: WorkflowNodeType
}

export const baseNode: LogicFlow.NodeConfig = {
  id: WorkflowNodeType.Base,
  type: WorkflowNodeType.Base,
  x: 260,
  y: 300,
  properties: {
    height: 728.375,
    stepName: '基本信息',
    config: {},
    node_data: {
      name: '',
      desc: '',
      prologue: '您好，我是您的智能助手，请问有什么可以帮助您？',
    },
    api_input_field_list: [],
    chat_input_field_list: [],
    user_input_field_list: [],
    showNode: true,
  },
}

export const startNode: LogicFlow.NodeConfig = {
  id: WorkflowNodeType.Start,
  type: WorkflowNodeType.Start,
  x: 680,
  y: 300,
  properties: {
    height: 364,
    stepName: '开始',
    config: {
      fields: [{ label: '用户问题', value: 'question' }],
      globalFields: [
        { label: '当前时间', value: 'time' },
        { label: '历史聊天记录', value: 'history_context' },
        { label: '对话 ID', value: 'chat_id' },
      ],
    },
    fields: [{ label: '用户问题', value: 'question' }],
    showNode: true,
  },
}

export const aiChatNode: WorkflowNodeDefinition = {
  type: WorkflowNodeType.AiChat,
  text: '与 AI 大模型进行对话',
  label: 'AI 对话',
  height: 500,
  properties: {
    stepName: 'AI 对话',
    config: {
      fields: [
        { label: 'AI 回答内容', value: 'answer' },
        { label: '思考过程', value: 'reasoning_content' },
        { label: '历史聊天记录', value: 'history_message' },
      ],
    },
    node_data: {
      model_id: '',
      model_id_reference: [],
      model_id_type: 'custom',
      model_setting: { reasoning_content_enable: false },
      prompt: '{{开始.question}}',
      system: '',
      is_result: true,
    },
    showNode: true,
  },
}

export const replyNode: WorkflowNodeDefinition = {
  type: WorkflowNodeType.Reply,
  text: '指定回复内容，引用变量会转换为字符串进行输出',
  label: '指定回复',
  height: 320,
  properties: {
    stepName: '指定回复',
    config: {
      fields: [{ label: '内容', value: 'answer' }],
    },
    node_data: {
      content: '',
      fields: [],
      is_result: true,
      reply_type: 'content',
    },
    showNode: true,
  },
}

export const BasicComponentsNode: Partial<Record<WorkflowNodeType, WorkflowNodeDefinition>> = {
  [WorkflowNodeType.AiChat]: aiChatNode,
  [WorkflowNodeType.Reply]: replyNode,
}

export const defaultNodes: LogicFlow.NodeConfig[] = [baseNode, startNode]

export const menuNodes = [
  {
    label: 'AI 能力',
    list: [aiChatNode],
  },
]

export const getMenuNodes = (workflowMode: WorkflowMode) => {
  if (workflowMode == WorkflowMode.Application) {
    return menuNodes
  }
  // if (workflowMode == WorkflowMode.ApplicationLoop) {
  //   return applicationLoopMenuNodes
  // }
  // if (workflowMode == WorkflowMode.Knowledge) {
  //   return knowledgeMenuNodes
  // }
  // if (workflowMode == WorkflowMode.KnowledgeLoop) {
  //   return knowledgeLoopMenuNodes
  // }
  // if (workflowMode == WorkflowMode.Tool) {
  //   return toolMenuNodes
  // }
  // if (workflowMode == WorkflowMode.ToolLoop) {
  //   return toolLoopMenuNodes
  // }
}
export const workflowModelDict: any = {
  [WorkflowMode.Application]: (node: any) => {
    return (
      ['application-node', 'tool-workflow-lib-node', 'tool-lib-node'].includes(node.type) &&
      node?.properties?.node_data?.tool_type !== 'DATA_SOURCE'
    )
  },
  [WorkflowMode.ApplicationLoop]: (node: any) => {
    return (
      ['application-node', 'tool-workflow-lib-node', 'tool-lib-node'].includes(node.type) &&
      node?.properties?.node_data?.tool_type !== 'DATA_SOURCE'
    )
  },
  [WorkflowMode.Knowledge]: (node: any) => {
    console.log(['tool-workflow-lib-node', 'tool-lib-node'].includes(node))
    return ['tool-workflow-lib-node', 'tool-lib-node'].includes(node.type)
  },
  [WorkflowMode.KnowledgeLoop]: (node: any) => {
    return (
      ['tool-workflow-lib-node', 'tool-lib-node'].includes(node.type) &&
      node?.properties?.node_data?.tool_type !== 'DATA_SOURCE'
    )
  },
  [WorkflowMode.Tool]: (node: any) => {
    return (
      ['tool-workflow-lib-node', 'tool-lib-node'].includes(node.type) &&
      node?.properties?.node_data?.tool_type !== 'DATA_SOURCE'
    )
  },
  [WorkflowMode.ToolLoop]: (node: any) => {
    return (
      ['tool-workflow-lib-node', 'tool-lib-node'].includes(node.type) &&
      node?.properties?.node_data?.tool_type !== 'DATA_SOURCE'
    )
  },
}

export function isLastNode(nodeModel: {
  graphModel: {
    getNodeIncomingNode: (nodeId: string) => unknown[]
    getNodeOutgoingNode: (nodeId: string) => unknown[]
  }
  id: string
}) {
  const incomingNodes = nodeModel.graphModel.getNodeIncomingNode(nodeModel.id)
  const outgoingNodes = nodeModel.graphModel.getNodeOutgoingNode(nodeModel.id)
  return incomingNodes.length > 0 && outgoingNodes.length === 0
}
