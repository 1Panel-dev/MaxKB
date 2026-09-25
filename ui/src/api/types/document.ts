import type { DOCUMENT_HIT_HANDLING } from '@/api/enums'
import type { KnowledgeType } from './knowledge'
export type DocumentHitHandling = (typeof DOCUMENT_HIT_HANDLING)[keyof typeof DOCUMENT_HIT_HANDLING]
/** 文档分页列表数据。 */
export interface DocumentItem {
  id: string
  knowledge_id: string
  name: string
  type: KnowledgeType
  is_active: boolean
  status: string
  status_meta?: Record<string, unknown>
  paragraph_count: number
  char_length: number
  hit_num: number
  hit_handling_method: DocumentHitHandling
  directly_return_similarity: number
  tags?: { id: string; key: string; value: string }[]
  meta?: Record<string, unknown>
  nick_name?: string | null
  create_time: string
  update_time: string
}
