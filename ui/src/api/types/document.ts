import type { DOCUMENT_HIT_HANDLING, DOCUMENT_TASK_STATE, DOCUMENT_TASK_TYPE } from '@/api/enums'
import type { KnowledgeGeneratePayload, KnowledgeType } from './knowledge'
export type DocumentHitHandling = (typeof DOCUMENT_HIT_HANDLING)[keyof typeof DOCUMENT_HIT_HANDLING]
export type DocumentTaskState = (typeof DOCUMENT_TASK_STATE)[keyof typeof DOCUMENT_TASK_STATE]
export type DocumentTaskType = (typeof DOCUMENT_TASK_TYPE)[keyof typeof DOCUMENT_TASK_TYPE]

/** 快速创建空白文档的请求数据。 */
export interface DocumentQuickCreatePayload {
  name: string
}

/** 文档召回及来源设置。 */
export interface DocumentSettingPayload {
  hit_handling_method: DocumentHitHandling
  directly_return_similarity: number
  meta?: Record<string, unknown>
  allow_download?: boolean
}

/** 根据文档分段生成问题。 */
export interface DocumentGeneratePayload extends KnowledgeGeneratePayload {
  document_id_list: string[]
}

/** 文件各任务的分段计数及状态发生时间。 */
export interface DocumentStatusMeta {
  aggs?: { status: string | null; count: number }[]
  state_time?: Partial<Record<DocumentTaskType, Partial<Record<DocumentTaskState, string>>>>
}

/** 文档分页列表数据。 */
export interface DocumentItem {
  id: string
  knowledge_id: string
  name: string
  type: KnowledgeType
  is_active: boolean
  status: string
  status_meta?: DocumentStatusMeta | null
  paragraph_count: number
  char_length: number
  hit_num: number
  hit_handling_method: DocumentHitHandling
  directly_return_similarity: number
  tags?: { id: string; key: string; value: string }[]
  tag_count?: number | null
  meta?: Record<string, unknown>
  nick_name?: string | null
  create_time: string
  update_time: string
}

/** 单个文档的局部更新字段。 */
export type DocumentUpdatePayload = Partial<Pick<DocumentItem, 'name' | 'is_active' | 'hit_handling_method' | 'directly_return_similarity' | 'meta'>>
