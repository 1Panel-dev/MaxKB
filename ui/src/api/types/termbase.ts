/** 知识库自定义分词条目。 */
export interface TermbaseItem {
  id: string
  knowledge_id: string
  content: string
  create_time: string
  update_time: string
}

/** 编辑单个自定义分词条目时提交的内容。 */
export interface TermbaseUpdatePayload {
  content: string
}
