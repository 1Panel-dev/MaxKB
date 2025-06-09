export enum SearchMode {
  embedding = 'views.application.form.dialog.vectorSearch',
  keywords = 'views.application.form.dialog.fullTextSearch',
  blend = 'views.application.form.dialog.hybridSearch'
}

export enum WorkflowType {
  Base = 'base-node',
  Start = 'start-node',
  AiChat = 'ai-chat-node',
  SearchDataset = 'search-dataset-node',
  Question = 'question-node',
  Condition = 'condition-node',
  Reply = 'reply-node',
  FunctionLib = 'function-lib-node',
  FunctionLibCustom = 'function-node',
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
