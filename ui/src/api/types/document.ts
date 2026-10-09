import type { DOCUMENT_HIT_HANDLING, DOCUMENT_TASK_STATE, DOCUMENT_TASK_TYPE } from '@/api/enums'
import type { DocumentStrategy, KnowledgeGeneratePayload, KnowledgeType } from './knowledge'
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

/** 文本解析结果及批量创建文档的载荷。 */
export interface DocumentImportParagraph {
  title?: string | null
  content: string
  problem_list?: { content: string }[]
}

export interface DocumentImportPayload {
  name: string
  source_file_id?: string | null
  doc_strategy: DocumentStrategy
  paragraphs: DocumentImportParagraph[]
}

export interface DocumentSplitResult extends Omit<DocumentImportPayload, 'paragraphs'> {
  content: DocumentImportParagraph[]
}

/** Web 地址导入及处理策略。 */
export interface WebDocumentImportPayload {
  source_url_list: string[]
  selector: string
  doc_strategy: DocumentStrategy
}

/** 飞书文件树节点，已导入文件不可重复选择。 */
export interface LarkDocumentNode {
  name: string
  token: string
  type: string
  is_exist: boolean
}

export interface LarkDocumentList {
  files: LarkDocumentNode[]
  has_more?: boolean
  next_page_token?: string
}

/** 保留 v2 飞书数组协议，每个文件附带处理策略。 */
export interface LarkDocumentImportPayload extends Pick<LarkDocumentNode, 'name' | 'token' | 'type'> {
  doc_strategy: DocumentStrategy
}
