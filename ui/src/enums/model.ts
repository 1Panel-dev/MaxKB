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
  EMBEDDING = t('views.template.model.EMBEDDING'),
  LLM = t('views.template.model.LLM'),
  STT = t('views.template.model.STT'),
  TTS = t('views.template.model.TTS'),
  IMAGE = t('views.template.model.IMAGE'),
  TTI = t('views.template.model.TTI'),
  RERANKER = t('views.template.model.RERANKER')
}
