/** Workspace 知识库列表和知识库卡片共用的业务类型。 */

import type LogicFlow from '@logicflow/core'
import { KNOWLEDGE_TYPE } from '@/api/enums'
import type { DefaultModelSettingPayload } from './model'

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

/** 知识库详情，工作流类型包含画布及发布状态。 */
export interface KnowledgeDetail extends KnowledgeItem {
  default_model_setting?: DefaultModelSettingPayload
  work_flow?: LogicFlow.GraphConfigData
  is_publish?: boolean
  publish_time?: string | null
}

/** 按标签名称分组的知识库标签。 */
export interface KnowledgeTagGroup {
  key: string
  values: { id: string; value: string; create_time: string; update_time: string }[]
}

/** 知识库工作流详情。 */
export interface KnowledgeWorkflowDetail {
  id: string
  knowledge: string
  workspace_id: string
  default_model_setting?: DefaultModelSettingPayload
  work_flow?: LogicFlow.GraphConfigData
  is_publish: boolean
  publish_time?: string | null
  create_time?: string
  update_time?: string
}
