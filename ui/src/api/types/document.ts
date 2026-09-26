import type { DOCUMENT_HIT_HANDLING, DOCUMENT_TASK_STATE, DOCUMENT_TASK_TYPE } from '@/api/enums'
import type { KnowledgeType } from './knowledge'
export type DocumentHitHandling = (typeof DOCUMENT_HIT_HANDLING)[keyof typeof DOCUMENT_HIT_HANDLING]
export type DocumentTaskState = (typeof DOCUMENT_TASK_STATE)[keyof typeof DOCUMENT_TASK_STATE]
export type DocumentTaskType = (typeof DOCUMENT_TASK_TYPE)[keyof typeof DOCUMENT_TASK_TYPE]

/** 文件各任务的分段计数及状态发生时间。 */
export interface DocumentStatusMeta {
  aggs?: { status: string; count: number }[]
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
