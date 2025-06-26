export enum SearchMode {
  embedding = 'views.application.dialog.vectorSearch',
  keywords = 'views.application.dialog.fullTextSearch',
  blend = 'views.application.dialog.hybridSearch'
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
  RrerankerNode = 'reranker-node',
  Application = 'application-node',
  DocumentExtractNode = 'document-extract-node',
  ImageUnderstandNode = 'image-understand-node',
  VariableAssignNode = 'variable-assign-node',
  FormNode = 'form-node',
  TextToSpeechNode = 'text-to-speech-node',
  SpeechToTextNode = 'speech-to-text-node',
  ImageGenerateNode = 'image-generate-node',
  McpNode = 'mcp-node',
}
