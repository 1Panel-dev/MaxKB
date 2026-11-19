import { computed, reactive } from 'vue'
import type { ShapeItem } from '@/workflow-canvas/types'
import { WorkflowMode, WorkflowNodeType } from '@/workflow-canvas/types'
import * as NodeData from '../config/node-data'
import { t } from '@/locales'

// 展示文案按节点类型读取，节点定义和保存数据保持原样。
export const WORKFLOW_NODE_DISPLAY: Partial<Record<WorkflowNodeType, { label: string; description: string }>> = reactive({
  [WorkflowNodeType.AiChat]: { label: computed(() => t('workflow.aiChat.label')), description: computed(() => t('workflow.aiChat.description')) },
  [WorkflowNodeType.Llm]: { label: computed(() => t('workflow.llm.label')), description: computed(() => t('workflow.llm.description')) },
  [WorkflowNodeType.IntentNode]: { label: computed(() => t('workflow.intent.label')), description: computed(() => t('workflow.intent.description')) },
  [WorkflowNodeType.SpeechToTextNode]: {
    label: computed(() => t('workflow.speechToText.label')),
    description: computed(() => t('workflow.speechToText.description')),
  },
  [WorkflowNodeType.TextToSpeechNode]: {
    label: computed(() => t('workflow.textToSpeech.label')),
    description: computed(() => t('workflow.textToSpeech.description')),
  },
  [WorkflowNodeType.ImageGenerateNode]: {
    label: computed(() => t('workflow.imageGenerate.label')),
    description: computed(() => t('workflow.imageGenerate.description')),
  },
  [WorkflowNodeType.ImageToVideoGenerateNode]: {
    label: computed(() => t('workflow.imageToVideo.label')),
    description: computed(() => t('workflow.imageToVideo.description')),
  },
  [WorkflowNodeType.TextToVideoGenerateNode]: {
    label: computed(() => t('workflow.textToVideo.label')),
    description: computed(() => t('workflow.textToVideo.description')),
  },
  [WorkflowNodeType.ImageUnderstandNode]: {
    label: computed(() => t('workflow.imageUnderstand.label')),
    description: computed(() => t('workflow.imageUnderstand.description')),
  },
  [WorkflowNodeType.VideoUnderstandNode]: {
    label: computed(() => t('workflow.videoUnderstand.label')),
    description: computed(() => t('workflow.videoUnderstand.description')),
  },
  [WorkflowNodeType.Question]: {
    label: computed(() => t('workflow.questionOptimization.label')),
    description: computed(() => t('workflow.questionOptimization.description')),
  },
  [WorkflowNodeType.Reply]: { label: computed(() => t('workflow.reply.label')), description: computed(() => t('workflow.reply.description')) },
  [WorkflowNodeType.Condition]: {
    label: computed(() => t('workflow.condition.label')),
    description: computed(() => t('workflow.condition.description')),
  },
  [WorkflowNodeType.FormNode]: { label: computed(() => t('workflow.form.label')), description: computed(() => t('workflow.form.description')) },
  [WorkflowNodeType.VariableAssignNode]: {
    label: computed(() => t('workflow.variableAssign.label')),
    description: computed(() => t('workflow.variableAssign.description')),
  },
  [WorkflowNodeType.VariableAggregationNode]: {
    label: computed(() => t('workflow.variableAggregation.label')),
    description: computed(() => t('workflow.variableAggregation.description')),
  },
  [WorkflowNodeType.VariableSplittingNode]: {
    label: computed(() => t('workflow.variableSplitting.label')),
    description: computed(() => t('workflow.variableSplitting.description')),
  },
  [WorkflowNodeType.ParameterExtractionNode]: {
    label: computed(() => t('workflow.parameterExtraction.label')),
    description: computed(() => t('workflow.parameterExtraction.description')),
  },
  [WorkflowNodeType.SearchKnowledge]: {
    label: computed(() => t('workflow.searchKnowledge.label')),
    description: computed(() => t('workflow.searchKnowledge.description')),
  },
  [WorkflowNodeType.SearchDocument]: {
    label: computed(() => t('workflow.searchDocument.label')),
    description: computed(() => t('workflow.searchDocument.description')),
  },
  [WorkflowNodeType.DocumentExtractNode]: {
    label: computed(() => t('workflow.documentExtract.label')),
    description: computed(() => t('workflow.documentExtract.description')),
  },
  [WorkflowNodeType.RerankerNode]: {
    label: computed(() => t('workflow.reranker.label')),
    description: computed(() => t('workflow.reranker.description')),
  },
  [WorkflowNodeType.McpNode]: { label: computed(() => t('workflow.mcp.label')), description: computed(() => t('workflow.mcp.description')) },
  [WorkflowNodeType.ToolLibCustom]: {
    label: computed(() => t('workflow.customTool.label')),
    description: computed(() => t('workflow.customTool.description')),
  },
  [WorkflowNodeType.LoopNode]: { label: computed(() => t('workflow.loop.label')), description: computed(() => t('workflow.loop.description')) },
  [WorkflowNodeType.LoopContinueNode]: {
    label: computed(() => t('workflow.loopContinue.label')),
    description: computed(() => t('workflow.loopContinue.description')),
  },
  [WorkflowNodeType.LoopBreakNode]: {
    label: computed(() => t('workflow.loopBreak.label')),
    description: computed(() => t('workflow.loopBreak.description')),
  },
  [WorkflowNodeType.DocumentSplitNode]: {
    label: computed(() => t('workflow.documentSplit.label')),
    description: computed(() => t('workflow.documentSplit.description')),
  },
  [WorkflowNodeType.DataSourceLocalNode]: {
    label: computed(() => t('workflow.localFile.label')),
    description: computed(() => t('workflow.localFile.description')),
  },
  [WorkflowNodeType.DataSourceWebNode]: {
    label: computed(() => t('workflow.webSource.label')),
    description: computed(() => t('workflow.webSource.description')),
  },
  [WorkflowNodeType.KnowledgeWriteNode]: {
    label: computed(() => t('workflow.knowledgeWrite.label')),
    description: computed(() => t('workflow.knowledgeWrite.description')),
  },
})

// 分组原名称供 AI 目录使用，界面读取对应的当前语言名称。
export const WORKFLOW_MENU_LABELS: Record<string, string> = reactive({
  数据源: computed(() => t('workflow.dataSource.label')),
  知识库: computed(() => t('knowledge.title')),
  'AI 能力': computed(() => t('workflow.menu.aiCapabilities')),
  业务逻辑: computed(() => t('workflow.menu.businessLogic')),
  数据处理: computed(() => t('workflow.menu.dataProcessing')),
  其他: computed(() => t('workflow.menu.other')),
})

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
    label: '知识库',
    list: [NodeData.searchKnowledgeNode, NodeData.searchDocumentNode, NodeData.rerankerNode, NodeData.documentExtractNode],
  },
  {
    label: '业务逻辑',
    list: [NodeData.conditionNode, NodeData.formNode, NodeData.replyNode, NodeData.loopNode],
  },
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
    label: '知识库',
    list: [NodeData.searchKnowledgeNode, NodeData.searchDocumentNode, NodeData.rerankerNode, NodeData.documentExtractNode],
  },
  {
    label: '业务逻辑',
    list: [NodeData.conditionNode, NodeData.formNode, NodeData.replyNode, NodeData.loopContinueNode, NodeData.loopBreakNode],
  },
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
    label: '业务逻辑',
    list: [NodeData.conditionNode, NodeData.replyNode, NodeData.loopContinueNode, NodeData.loopBreakNode],
  },
  {
    label: '数据处理',
    list: [NodeData.variableAssignNode, NodeData.variableAggregationNode, NodeData.variableSplittingNode, NodeData.parameterExtractionNode],
  },
  { label: '其他', list: [NodeData.mcpNode, NodeData.toolCustomNode] },
]
export const toolLoopMenuNodes = [
  { label: '数据源', list: [NodeData.dataSourceLocalNode, NodeData.dataSourceWebNode] },
  {
    label: '知识库',
    list: [NodeData.searchKnowledgeNode, NodeData.documentSplitNode, NodeData.knowledgeWriteNode, NodeData.documentExtractNode],
  },
  {
    label: 'AI 能力',
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
    label: '业务逻辑',
    list: [NodeData.conditionNode, NodeData.formNode, NodeData.replyNode, NodeData.loopContinueNode, NodeData.loopBreakNode],
  },
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
    label: '知识库',
    list: [
      NodeData.searchKnowledgeNode,
      NodeData.searchDocumentNode,
      NodeData.rerankerNode,
      NodeData.documentExtractNode,
      NodeData.documentSplitNode,
    ],
  },
  {
    label: '业务逻辑',
    list: [NodeData.conditionNode, NodeData.formNode, NodeData.replyNode, NodeData.loopNode],
  },
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
