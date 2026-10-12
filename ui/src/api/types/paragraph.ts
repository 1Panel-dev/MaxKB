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
}

export interface ParagraphQuery {
  title?: string
  content?: string
}

export interface ParagraphCreatePayload {
  title: string
  content: string
  is_active: boolean
}
