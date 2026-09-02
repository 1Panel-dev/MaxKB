import LogicFlow from '@logicflow/core'
/** LogicFlow 节点类型，作为工作流图数据中的稳定协议值。 */
export enum WorkflowNodeType {
  Base = 'base-node',
  KnowledgeBase = 'knowledge-base-node',
  Start = 'start-node',
  AiChat = 'ai-chat-node',
  SearchKnowledge = 'search-knowledge-node',
  SearchDocument = 'search-document-node',
  Question = 'question-node',
  Condition = 'condition-node',
  Reply = 'reply-node',
  ToolLib = 'tool-lib-node',
  ToolWorkflowLib = 'tool-workflow-lib-node',
  ToolLibCustom = 'tool-custom-node',
  RerankerNode = 'reranker-node',
  Application = 'application-node',
  DocumentExtractNode = 'document-extract-node',
  DocumentSplitNode = 'document-split-node',
  ImageUnderstandNode = 'image-understand-node',
  VariableAssignNode = 'variable-assign-node',
  FormNode = 'form-node',
  TextToSpeechNode = 'text-to-speech-node',
  SpeechToTextNode = 'speech-to-text-node',
  ImageGenerateNode = 'image-generate-node',
  McpNode = 'mcp-node',
  IntentNode = 'intent-node',
  TextToVideoGenerateNode = 'text-to-video-node',
  ImageToVideoGenerateNode = 'image-to-video-node',
  LoopNode = 'loop-node',
  LoopBodyNode = 'loop-body-node',
  LoopStartNode = 'loop-start-node',
  LoopContinueNode = 'loop-continue-node',
  LoopBreakNode = 'loop-break-node',
  VariableSplittingNode = 'variable-splitting-node',
  VariableAggregationNode = 'variable-aggregation-node',
  VideoUnderstandNode = 'video-understand-node',
  ParameterExtractionNode = 'parameter-extraction-node',
  DataSourceLocalNode = 'data-source-local-node',
  DataSourceWebNode = 'data-source-web-node',
  KnowledgeWriteNode = 'knowledge-write-node',
  ToolStartNode = 'tool-start-node',
  ToolBaseNode = 'tool-base-node',
}

export enum WorkflowKind {
  DataSource = 'data-source',
}
export enum WorkflowMode {
  // 应用工作流
  Application = 'application',
  // 应用工作流循环
  ApplicationLoop = 'application-loop',
  // 知识库工作流
  Knowledge = 'knowledge',
  // 工具
  Tool = 'tool',
  // 工具循环体
  ToolLoop = 'tool-loop',
  // 知识库工作流循环体
  KnowledgeLoop = 'knowledge-loop',
}

export interface WorkflowNodeField {
  children?: WorkflowNodeField[]
  label: string
  type?: string
  value: string
}
export type ShapeItem = {
  callback?: (logicFlow: LogicFlow, container?: HTMLElement) => void
  className?: string
  disabled?: boolean
  icon?: string
  label?: string
  properties?: LogicFlow.PropertiesType
  text?: string
  type?: string
}
