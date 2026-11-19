import { computed, reactive } from 'vue'
import type { ShapeItem } from '@/workflow-canvas/types'
import { WorkflowMode, WorkflowNodeType } from '@/workflow-canvas/types'
import * as NodeData from '../config/node-data'
import { t } from '@/locales'

export interface WorkflowMenuNode extends ShapeItem {
  height?: number
  label: string
  type: WorkflowNodeType
}

export interface WorkflowMenuGroup {
  label: string
  list: WorkflowMenuNode[]
}
export const knowledgeMenuNodes = reactive([
  { label: computed(() => t('resource.dataSource.label')), list: [NodeData.dataSourceLocalNode, NodeData.dataSourceWebNode] },
  { label: computed(() => t('knowledge.title')), list: [NodeData.documentSplitNode, NodeData.knowledgeWriteNode, NodeData.documentExtractNode] },
  {
    label: computed(() => t('workflow.menu.aiCapabilities')),
    list: [
      NodeData.aiChatNode,
      NodeData.llmNode,
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
  { label: computed(() => t('workflow.menu.businessLogic')), list: [NodeData.conditionNode, NodeData.replyNode, NodeData.loopNode] },
  {
    label: computed(() => t('workflow.menu.dataProcessing')),
    list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode],
  },
  { label: computed(() => t('workflow.menu.other')), list: [NodeData.mcpNode, NodeData.toolCustomNode] },
])
export const menuNodes = reactive([
  {
    label: computed(() => t('workflow.menu.aiCapabilities')),
    list: [
      NodeData.aiChatNode,
      NodeData.llmNode,
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
    label: computed(() => t('knowledge.title')),
    list: [NodeData.searchKnowledgeNode, NodeData.searchDocumentNode, NodeData.rerankerNode, NodeData.documentExtractNode],
  },
  {
    label: computed(() => t('workflow.menu.businessLogic')),
    list: [NodeData.conditionNode, NodeData.formNode, NodeData.replyNode, NodeData.loopNode],
  },
  {
    label: computed(() => t('workflow.menu.dataProcessing')),
    list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode],
  },
  { label: computed(() => t('workflow.menu.other')), list: [NodeData.mcpNode, NodeData.toolCustomNode] },
])
export const applicationLoopMenuNodes = reactive([
  {
    label: computed(() => t('workflow.menu.aiCapabilities')),
    list: [
      NodeData.aiChatNode,
      NodeData.llmNode,
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
    label: computed(() => t('knowledge.title')),
    list: [NodeData.searchKnowledgeNode, NodeData.searchDocumentNode, NodeData.rerankerNode, NodeData.documentExtractNode],
  },
  {
    label: computed(() => t('workflow.menu.businessLogic')),
    list: [NodeData.conditionNode, NodeData.formNode, NodeData.replyNode, NodeData.loopContinueNode, NodeData.loopBreakNode],
  },
  {
    label: computed(() => t('workflow.menu.dataProcessing')),
    list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode],
  },
  { label: computed(() => t('workflow.menu.other')), list: [NodeData.mcpNode, NodeData.toolCustomNode] },
])
export const knowledgeLoopMenuNodes = reactive([
  { label: computed(() => t('resource.dataSource.label')), list: [NodeData.dataSourceLocalNode, NodeData.dataSourceWebNode] },
  { label: computed(() => t('knowledge.title')), list: [NodeData.documentSplitNode, NodeData.knowledgeWriteNode, NodeData.documentExtractNode] },
  {
    label: computed(() => t('workflow.menu.aiCapabilities')),
    list: [
      NodeData.aiChatNode,
      NodeData.llmNode,
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
    label: computed(() => t('workflow.menu.businessLogic')),
    list: [NodeData.conditionNode, NodeData.replyNode, NodeData.loopContinueNode, NodeData.loopBreakNode],
  },
  {
    label: computed(() => t('workflow.menu.dataProcessing')),
    list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode],
  },
  { label: computed(() => t('workflow.menu.other')), list: [NodeData.mcpNode, NodeData.toolCustomNode] },
])
export const toolLoopMenuNodes = reactive([
  { label: computed(() => t('resource.dataSource.label')), list: [NodeData.dataSourceLocalNode, NodeData.dataSourceWebNode] },
  {
    label: computed(() => t('knowledge.title')),
    list: [NodeData.searchKnowledgeNode, NodeData.documentSplitNode, NodeData.knowledgeWriteNode, NodeData.documentExtractNode],
  },
  {
    label: computed(() => t('workflow.menu.aiCapabilities')),
    list: [
      NodeData.aiChatNode,
      NodeData.llmNode,
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
    label: computed(() => t('workflow.menu.businessLogic')),
    list: [NodeData.conditionNode, NodeData.formNode, NodeData.replyNode, NodeData.loopContinueNode, NodeData.loopBreakNode],
  },
  {
    label: computed(() => t('workflow.menu.dataProcessing')),
    list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode],
  },
  { label: computed(() => t('workflow.menu.other')), list: [NodeData.mcpNode, NodeData.toolCustomNode] },
])
const toolMenuNodes = reactive([
  {
    label: computed(() => t('workflow.menu.aiCapabilities')),
    list: [
      NodeData.aiChatNode,
      NodeData.llmNode,
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
    label: computed(() => t('knowledge.title')),
    list: [
      NodeData.searchKnowledgeNode,
      NodeData.searchDocumentNode,
      NodeData.rerankerNode,
      NodeData.documentExtractNode,
      NodeData.documentSplitNode,
    ],
  },
  {
    label: computed(() => t('workflow.menu.businessLogic')),
    list: [NodeData.conditionNode, NodeData.formNode, NodeData.replyNode, NodeData.loopNode],
  },
  {
    label: computed(() => t('workflow.menu.dataProcessing')),
    list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode],
  },
  { label: computed(() => t('workflow.menu.other')), list: [NodeData.mcpNode, NodeData.toolCustomNode] },
])
const menuNodesByMode: Record<WorkflowMode, WorkflowMenuGroup[]> = {
  [WorkflowMode.Application]: menuNodes,
  [WorkflowMode.ApplicationLoop]: applicationLoopMenuNodes,
  [WorkflowMode.Knowledge]: knowledgeMenuNodes,
  [WorkflowMode.KnowledgeLoop]: knowledgeLoopMenuNodes,
  [WorkflowMode.Tool]: toolMenuNodes,
  [WorkflowMode.ToolLoop]: toolLoopMenuNodes,
}

export const getMenuNodes = (workflowMode: WorkflowMode): WorkflowMenuGroup[] => menuNodesByMode[workflowMode]
