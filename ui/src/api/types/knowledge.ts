/** Workspace 知识库列表和知识库卡片共用的业务类型。 */

import { KNOWLEDGE_TYPE } from '@/api/enums'

export type KnowledgeType = (typeof KNOWLEDGE_TYPE)[keyof typeof KNOWLEDGE_TYPE]

export interface KnowledgeItem {
  application_mapping_count?: number
  char_length?: number | null
  create_time?: string
  desc?: string | null
  document_count?: number | null
  embedding_model_id?: string | null
  file_count_limit?: number
  file_size_limit?: number
  folder_id?: string
  id: string
  image_count?: number | null
  meta?: Record<string, unknown>
  name: string
  nick_name?: string | null
  scope?: string
  type: KnowledgeType
  update_time?: string
  user_id?: string | null
  workspace_id: string
}
