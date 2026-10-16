import type { RelatedQuestionsConfig } from './knowledge'

/** 文档分段的查询响应与新增载荷。 */
export interface ParagraphItem {
  id: string
  document_id: string
  title: string | null
  content: string
  position: number
  is_active: boolean
  create_time: string
  update_time: string
  hit_num: number
  last_hit_time: string | null
}

/** 分段关联的问题及详情。 */
export interface ParagraphProblem {
  id: string
  content: string
}

/** 从问题详情查询到的关联分段，额外携带所属知识库与文档名称。 */
export interface ProblemParagraph extends ParagraphItem {
  knowledge_id: string
  document_name: string
}

/** 批量将问题关联到文档分段时使用的分段引用。 */
export interface ProblemParagraphReference {
  paragraph_id: string
  document_id: string
}

/** 批量关联问题与文档分段的请求载荷。 */
export interface ProblemBatchAssociationPayload {
  problem_id_list: string[]
  paragraph_list: ProblemParagraphReference[]
}

export interface ParagraphDetail extends ParagraphItem {
  problem_list: ParagraphProblem[]
  source_file_id?: string | null
}

export interface ParagraphUpdatePayload {
  title: string
  content: string
}

/** 保存正文或单独更新分段启用状态。 */
export type ParagraphEditPayload = Partial<ParagraphUpdatePayload & Pick<ParagraphItem, 'is_active'>>

export interface ParagraphQuery {
  title?: string
  content?: string
}

export interface ParagraphCreatePayload {
  title: string
  content: string
  is_active: boolean
  position?: number
  problem_list?: { content: string }[]
}

/** 为选中的分段生成关联问题。 */
export interface ParagraphGeneratePayload extends RelatedQuestionsConfig {
  paragraph_id_list: string[]
}
