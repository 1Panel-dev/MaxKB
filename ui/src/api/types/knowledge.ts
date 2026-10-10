/** Workspace 知识库列表和知识库卡片共用的业务类型。 */

import type LogicFlow from '@logicflow/core'
import { KNOWLEDGE_SYNC_TYPE, KNOWLEDGE_TYPE } from '@/api/enums'
import type { DefaultModelSettingPayload } from './model'
import type { DocumentTaskState } from './document'

/** 生成关联问题共用的模型与提示词配置。 */
export interface RelatedQuestionsConfig {
  model_id: string
  model_params_setting: Record<string, unknown>
  prompt: string
}

/** 对知识库中指定任务状态的分段生成关联问题。 */
export interface KnowledgeGeneratePayload extends RelatedQuestionsConfig {
  state_list: DocumentTaskState[]
}

export type KnowledgeType = (typeof KNOWLEDGE_TYPE)[keyof typeof KNOWLEDGE_TYPE]

export type KnowledgeSyncType = (typeof KNOWLEDGE_SYNC_TYPE)[keyof typeof KNOWLEDGE_SYNC_TYPE]

export interface KnowledgeItem {
  application_mapping_count?: number
  char_length?: number | null
  create_time?: string
  desc?: string | null
  doc_strategy?: DocumentStrategy | null
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
  values: { id: string; value: string; doc_count?: number; create_time: string; update_time: string }[]
}

/** 创建知识库标签的名称和值。 */
export interface KnowledgeTagPayload {
  key: string
  value: string
}

/** 编辑单个知识库标签，保留现有接口的 ID 字段。 */
export interface KnowledgeTagUpdatePayload extends KnowledgeTagPayload {
  id: string
}

/** 知识库工作流任务状态。 */
export type KnowledgeWorkflowActionState = 'STARTED' | 'PENDING' | 'SUCCESS' | 'FAILURE' | 'REVOKE' | 'REVOKED'

/** 知识库工作流执行记录摘要。 */
export interface KnowledgeExecutionRecord {
  id: string
  knowledge_id: string
  state: KnowledgeWorkflowActionState
  run_time?: number | null
  create_time?: string
  meta?: Record<string, unknown> & { user_name?: string }
}

/** 知识库工作流执行详情，调试与历史记录共用。 */
export interface KnowledgeWorkflowAction extends KnowledgeExecutionRecord {
  details: Record<string, Record<string, unknown>>
}

/** 知识库工作流调试提交参数。 */
export interface KnowledgeWorkflowDebugPayload {
  data_source: Record<string, unknown>
  knowledge_base: Record<string, unknown>
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

/** 创建知识库共用的基本信息。 */
export interface KnowledgeCreatePayload {
  name: string
  desc: string
  embedding_model_id: string
  folder_id: string
  type: KnowledgeType
}

/** 创建工作流知识库的请求参数。 */
export interface KnowledgeWorkflowCreatePayload extends KnowledgeCreatePayload {
  work_flow: LogicFlow.GraphConfigData
  work_flow_template?: KnowledgeWorkflowTemplate
}

/** Web 文档分段、视觉处理和索引策略。 */
export interface DocumentStrategy {
  split: { mode: 'smart' | 'advanced'; patterns: string[] | null; min_length: number; max_length: number; child_length: number; auto_clean: boolean }
  visual: { enabled: boolean; strategy: 'model' | 'tool'; model_id: string | null; tool_id: string | null }
  index: { title_as_question: boolean }
}

/** 创建 Web 知识库的站点配置。 */
export interface WebKnowledgeCreatePayload extends KnowledgeCreatePayload {
  source_url: string
  selector: string
  doc_strategy?: DocumentStrategy
}

/** 创建飞书知识库的应用配置。 */
export interface LarkKnowledgeCreatePayload extends KnowledgeCreatePayload {
  app_id: string
  app_secret: string
  folder_token: string
}

/** 知识库工作流商店模板。 */
export interface KnowledgeWorkflowTemplate {
  downloadUrl: string
  downloadCallbackUrl?: string
}

/** 知识库工作流模板商店响应。 */
export interface KnowledgeWorkflowStoreResponse {
  additionalProperties: { tags: { key: string; name: string }[] }
  apps: import('./workflow-template').WorkflowStoreTemplate[]
}
