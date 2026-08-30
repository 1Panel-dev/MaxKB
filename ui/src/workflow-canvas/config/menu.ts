import { WorkflowMode, WorkflowNodeType } from '@/workflow-canvas/types'
import * as NodeData from './node-data'
interface WorkflowMenuNode {
  type: WorkflowNodeType
}
interface WorkflowMenuGroup {
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
  { label: '数据处理', list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode] },
  { label: '其他', list: [NodeData.mcpNode, NodeData.toolNode] },
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
  { label: '数据处理', list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode] },
  { label: '其他', list: [NodeData.mcpNode, NodeData.toolNode] },
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
  { label: '数据处理', list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode] },
  { label: '其他', list: [NodeData.mcpNode, NodeData.toolNode] },
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
  { label: '数据处理', list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode] },
  { label: '其他', list: [NodeData.mcpNode, NodeData.toolNode] },
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
  { label: '数据处理', list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode] },
  { label: '其他', list: [NodeData.mcpNode, NodeData.toolNode] },
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
  { label: '知识库', list: [NodeData.searchKnowledgeNode, NodeData.searchDocumentNode, NodeData.rerankerNode, NodeData.documentExtractNode, NodeData.documentSplitNode] },
  { label: '业务逻辑', list: [NodeData.conditionNode, NodeData.formNode, NodeData.replyNode, NodeData.loopNode] },
  { label: '数据处理', list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode] },
  { label: '其他', list: [NodeData.mcpNode, NodeData.toolNode] },
]
export const getMenuNodes = (workflowMode: WorkflowMode): WorkflowMenuGroup[] | undefined => {
  if (workflowMode == WorkflowMode.Application) {
    return menuNodes
  }
  if (workflowMode == WorkflowMode.ApplicationLoop) {
    return applicationLoopMenuNodes
  }
  if (workflowMode == WorkflowMode.Knowledge) {
    return knowledgeMenuNodes
  }
  if (workflowMode == WorkflowMode.KnowledgeLoop) {
    return knowledgeLoopMenuNodes
  }
  if (workflowMode == WorkflowMode.Tool) {
    return toolMenuNodes
  }
  if (workflowMode == WorkflowMode.ToolLoop) {
    return toolLoopMenuNodes
  }
}
