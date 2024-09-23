export enum PermissionType {
  PRIVATE = '私有',
  PUBLIC = '公用'
}
export enum PermissionDesc {
  PRIVATE = '仅当前用户使用',
  PUBLIC = '所有用户都可使用，不能编辑'
}

export enum modelType {
  EMBEDDING = '向量模型',
  LLM = '大语言模型',
  STT = '语音识别',
  TTS = '语音合成',
  RERANKER = '重排模型'
}
