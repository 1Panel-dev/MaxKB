/** Workspace 智能体列表及其卡片共用的业务类型。 */

import type LogicFlow from '@logicflow/core'
import { APPLICATION_ACCESS_PLATFORM, APPLICATION_TYPE } from '@/api/enums'
import type { DefaultModelSettingPayload } from './model'
import type { WorkflowStoreTemplate } from './workflow-template'
import type { Dict } from './common'
import type { KnowledgeItem } from './knowledge'

export type ApplicationType = (typeof APPLICATION_TYPE)[keyof typeof APPLICATION_TYPE]

export type ApplicationAccessPlatform = (typeof APPLICATION_ACCESS_PLATFORM)[keyof typeof APPLICATION_ACCESS_PLATFORM]

/** 状态数组依次为是否已配置、是否启用；未配置的平台可能不返回。 */
export type ApplicationAccessStatus = Partial<Record<ApplicationAccessPlatform, [exists: boolean, isActive: boolean]>>

export interface ApplicationAccessConfig extends Dict<string | boolean | undefined> {
  callback_url?: string
  is_certification?: boolean
}

export interface ApplicationAccessStatusPayload {
  type: ApplicationAccessPlatform
  status: boolean
}

export interface ApplicationDetail extends Omit<ApplicationFormPayload, 'desc'> {
  /** 详情接口返回的主模型 ID。 */
  model?: string | null
  stt_model?: string | null
  tts_model?: string | null
  long_term_model?: string | null
  knowledge_list?: KnowledgeItem[]
  default_model_setting?: DefaultModelSettingPayload
  create_time?: string
  desc?: string | null
  folder?: string
  folder_id?: string
  icon?: string
  id: string
  is_portal: boolean
  is_publish: boolean
  name: string
  nick_name?: string | null
  publish_time?: string | null
  resource_count?: number
  resource_type: string
  type: ApplicationType
  update_time?: string
  user_id?: string | null
  workspace_id?: string
  work_flow?: LogicFlow.GraphConfigData
}

export interface ApplicationFormPayload {
  clean_time?: number
  file_clean_time?: number
  default_model_setting?: DefaultModelSettingPayload
  name?: string
  desc?: string
  model_id?: string
  dialogue_number?: number
  prologue?: string
  knowledge_id_list?: string[]
  knowledge_setting?: Record<string, unknown>
  model_setting?: Record<string, unknown>
  problem_optimization?: boolean
  problem_optimization_prompt?: string
  icon?: string
  type?: ApplicationType
  work_flow?: LogicFlow.GraphConfigData
  model_params_setting?: Record<string, unknown>
  tts_model_params_setting?: Record<string, unknown>
  stt_model_params_setting?: Record<string, unknown>
  stt_model_id?: string | null
  tts_model_id?: string | null
  stt_model_enable?: boolean
  tts_model_enable?: boolean
  tts_type?: string
  tts_autoplay?: boolean
  stt_autosend?: boolean
  folder_id?: string
  workspace_id?: string
  mcp_enable?: boolean
  mcp_servers?: string
  mcp_tool_ids?: string[]
  mcp_source?: string
  tool_enable?: boolean
  tool_ids?: string[]
  application_enable?: boolean
  application_ids?: string[]
  skill_tool_ids?: string[]
  mcp_output_enable?: boolean
  work_flow_template?: Record<string, unknown>
  long_term_enable?: boolean
  long_term_model_id?: string | null
  long_term_model_params_setting?: Record<string, unknown>
  long_term_trigger_setting?: Record<string, unknown>
  long_term_trigger_type?: string
}

export interface PromptGenerateMessage {
  content: string
  role: 'ai' | 'user'
}

export interface PromptGeneratePayload {
  messages: PromptGenerateMessage[]
  prompt: string
  model_params_setting?: Record<string, unknown>
}

/** 通用流式补全的 OpenAI 格式消息（工作流 AI 生成的 agent 循环使用）。 */
export interface ChatCompletionMessage {
  role: 'system' | 'user' | 'assistant' | 'tool'
  content: string
  tool_calls?: Array<{ id: string; type: string; function: { name: string; arguments: string } }>
  tool_call_id?: string
  reasoning_content?: string
}

export interface ChatCompletionPayload {
  messages: ChatCompletionMessage[]
  tools?: Array<{ type: 'function'; function: { name: string; description: string; parameters: Record<string, unknown> } }>
  model_params_setting?: Record<string, unknown>
}

/** 智能体模板复用工作流模板的展示与下载元数据。 */
export type ApplicationStoreTemplate = WorkflowStoreTemplate

export interface ApplicationStoreResponse {
  additionalProperties: { tags: { key: string; name: string }[] }
  apps: ApplicationStoreTemplate[]
}

/** 智能体概览的用户 Tokens 消耗，接口返回完整排行。 */
export interface ApplicationTokenUsage {
  username: string
  token_usage: number | null
}

/** 智能体概览的用户提问次数，接口返回完整排行。 */
export interface ApplicationTopQuestion {
  username: string
  chat_record_count: number
}
