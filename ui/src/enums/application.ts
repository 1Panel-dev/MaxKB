export enum SearchMode {
  embedding = 'views.application.dialog.vectorSearch',
  keywords = 'views.application.dialog.fullTextSearch',
  blend = 'views.application.dialog.hybridSearch',
}

export enum WorkflowType {
  Base = 'base-node',
  Start = 'start-node',
  AiChat = 'ai-chat-node',
  SearchKnowledge = 'search-knowledge-node',
  Question = 'question-node',
  Condition = 'condition-node',
  Reply = 'reply-node',
  ToolLib = 'tool-lib-node',
  ToolLibCustom = 'tool-node',
  RerankerNode = 'reranker-node',
  Application = 'application-node',
  DocumentExtractNode = 'document-extract-node',
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
}
export enum WorkflowMode {
  // 应用工作流
  Application = 'application',
  // 应用工作流循环
  ApplicationLoop = 'application-loop',
}
