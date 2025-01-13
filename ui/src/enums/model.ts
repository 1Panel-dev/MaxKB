import { t } from '@/locales'
export enum PermissionType {
  PRIVATE = '私有',
  PUBLIC = '公用'
}
export enum PermissionDesc {
  PRIVATE = '仅当前用户使用',
  PUBLIC = '所有用户都可使用，不能编辑'
}

export enum modelType {
  EMBEDDING = 'views.template.model.EMBEDDING',
  LLM = 'views.template.model.LLM',
  STT = 'views.template.model.STT',
  TTS = 'views.template.model.TTS',
  IMAGE = 'views.template.model.IMAGE',
  TTI = 'views.template.model.TTI',
  RERANKER = 'views.template.model.RERANKER'
}
