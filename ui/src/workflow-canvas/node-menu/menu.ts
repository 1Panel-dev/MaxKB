import { WorkflowMode, WorkflowNodeType, type ShapeItem } from '@/workflow-canvas/types'
import * as NodeData from '../config/node-data'

export interface WorkflowMenuNode extends ShapeItem {
  height?: number
  label: string
  type: WorkflowNodeType
}

export interface WorkflowMenuGroup {
  label: string
  list: WorkflowMenuNode[]
}
export const knowledgeMenuNodes = [
  { label: '数据源', list: [NodeData.dataSourceLocalNode, NodeData.dataSourceWebNode] },
  { label: '知识库', list: [NodeData.documentSplitNode, NodeData.knowledgeWriteNode, NodeData.documentExtractNode] },
  {
    label: 'AI 能力',
    list: [
      NodeData.aiChatNode,
      NodeData.intentNode,
      NodeData.textToSpeechNode,
      NodeData.speechToTextNode,
      NodeData.imageGenerateNode,
      NodeData.imageUnderstandNode,
      NodeData.textToVideoNode,
      NodeData.imageToVideoNode,
      NodeData.videoUnderstandNode,
      NodeData.questionNode,
    ],
  },
  { label: '业务逻辑', list: [NodeData.conditionNode, NodeData.replyNode, NodeData.loopNode] },
  {
    label: '数据处理',
    list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode],
  },
  { label: '其他', list: [NodeData.mcpNode, NodeData.toolCustomNode] },
]
export const menuNodes = [
  {
    label: 'AI 能力',
    list: [
      NodeData.aiChatNode,
      NodeData.intentNode,
      NodeData.textToSpeechNode,
      NodeData.speechToTextNode,
      NodeData.imageGenerateNode,
      NodeData.imageUnderstandNode,
      NodeData.textToVideoNode,
      NodeData.imageToVideoNode,
      NodeData.videoUnderstandNode,
      NodeData.questionNode,
    ],
  },
  { label: '知识库', list: [NodeData.searchKnowledgeNode, NodeData.searchDocumentNode, NodeData.rerankerNode, NodeData.documentExtractNode] },
  { label: '业务逻辑', list: [NodeData.conditionNode, NodeData.formNode, NodeData.replyNode, NodeData.loopNode] },
  {
    label: '数据处理',
    list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode],
  },
  { label: '其他', list: [NodeData.mcpNode, NodeData.toolCustomNode] },
]
export const applicationLoopMenuNodes = [
  {
    label: 'AI 能力',
    list: [
      NodeData.aiChatNode,
      NodeData.intentNode,
      NodeData.textToSpeechNode,
      NodeData.speechToTextNode,
      NodeData.imageGenerateNode,
      NodeData.imageUnderstandNode,
      NodeData.textToVideoNode,
      NodeData.imageToVideoNode,
      NodeData.videoUnderstandNode,
      NodeData.questionNode,
    ],
  },
  { label: '知识库', list: [NodeData.searchKnowledgeNode, NodeData.searchDocumentNode, NodeData.rerankerNode, NodeData.documentExtractNode] },
  { label: '业务逻辑', list: [NodeData.conditionNode, NodeData.formNode, NodeData.replyNode, NodeData.loopContinueNode, NodeData.loopBreakNode] },
  {
    label: '数据处理',
    list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode],
  },
  { label: '其他', list: [NodeData.mcpNode, NodeData.toolCustomNode] },
]
export const knowledgeLoopMenuNodes = [
  { label: '数据源', list: [NodeData.dataSourceLocalNode, NodeData.dataSourceWebNode] },
  { label: '知识库', list: [NodeData.documentSplitNode, NodeData.knowledgeWriteNode, NodeData.documentExtractNode] },
  {
    label: 'AI 能力',
    list: [
      NodeData.aiChatNode,
      NodeData.intentNode,
      NodeData.textToSpeechNode,
      NodeData.speechToTextNode,
      NodeData.imageGenerateNode,
      NodeData.imageUnderstandNode,
      NodeData.textToVideoNode,
      NodeData.imageToVideoNode,
      NodeData.videoUnderstandNode,
      NodeData.questionNode,
    ],
  },
  { label: '业务逻辑', list: [NodeData.conditionNode, NodeData.replyNode, NodeData.loopContinueNode, NodeData.loopBreakNode] },
  {
    label: '数据处理',
    list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode],
  },
  { label: '其他', list: [NodeData.mcpNode, NodeData.toolCustomNode] },
]
export const toolLoopMenuNodes = [
  { label: '数据源', list: [NodeData.dataSourceLocalNode, NodeData.dataSourceWebNode] },
  { label: '知识库', list: [NodeData.documentSplitNode, NodeData.knowledgeWriteNode, NodeData.documentExtractNode] },
  {
    label: 'AI 能力',
    list: [
      NodeData.aiChatNode,
      NodeData.intentNode,
      NodeData.textToSpeechNode,
      NodeData.speechToTextNode,
      NodeData.imageGenerateNode,
      NodeData.imageUnderstandNode,
      NodeData.textToVideoNode,
      NodeData.imageToVideoNode,
      NodeData.videoUnderstandNode,
      NodeData.questionNode,
    ],
  },
  { label: '业务逻辑', list: [NodeData.conditionNode, NodeData.formNode, NodeData.replyNode, NodeData.loopContinueNode, NodeData.loopBreakNode] },
  {
    label: '数据处理',
    list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode],
  },
  { label: '其他', list: [NodeData.mcpNode, NodeData.toolCustomNode] },
]
const toolMenuNodes = [
  {
    label: 'AI 能力',
    list: [
      NodeData.aiChatNode,
      NodeData.intentNode,
      NodeData.textToSpeechNode,
      NodeData.speechToTextNode,
      NodeData.imageGenerateNode,
      NodeData.imageUnderstandNode,
      NodeData.textToVideoNode,
      NodeData.imageToVideoNode,
      NodeData.videoUnderstandNode,
      NodeData.questionNode,
    ],
  },
  {
    label: '知识库',
    list: [
      NodeData.searchKnowledgeNode,
      NodeData.searchDocumentNode,
      NodeData.rerankerNode,
      NodeData.documentExtractNode,
      NodeData.documentSplitNode,
    ],
  },
  { label: '业务逻辑', list: [NodeData.conditionNode, NodeData.formNode, NodeData.replyNode, NodeData.loopNode] },
  {
    label: '数据处理',
    list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode],
  },
  { label: '其他', list: [NodeData.mcpNode, NodeData.toolCustomNode] },
]
const menuNodesByMode: Record<WorkflowMode, WorkflowMenuGroup[]> = {
  [WorkflowMode.Application]: menuNodes,
  [WorkflowMode.ApplicationLoop]: applicationLoopMenuNodes,
  [WorkflowMode.Knowledge]: knowledgeMenuNodes,
  [WorkflowMode.KnowledgeLoop]: knowledgeLoopMenuNodes,
  [WorkflowMode.Tool]: toolMenuNodes,
  [WorkflowMode.ToolLoop]: toolLoopMenuNodes,
}

export const getMenuNodes = (workflowMode: WorkflowMode): WorkflowMenuGroup[] => menuNodesByMode[workflowMode]
