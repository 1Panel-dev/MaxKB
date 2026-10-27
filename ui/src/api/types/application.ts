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

/** 智能体展示设置；图片响应为 URL，保存时通过 FormData 分别提交文件及原 URL。 */
export interface ApplicationDisplaySetting {
  show_source: boolean
  show_exec: boolean
  language: string
  show_history: boolean
  draggable: boolean
  show_share: boolean
  icon: string
  chat_background: string
  avatar: string
  float_icon: string
  user_avatar: string
  disclaimer: boolean
  disclaimer_value: string
  custom_theme: { theme_color: string; header_font_color: string }
  float_location: {
    x: { type: 'left' | 'right'; value: number }
    y: { type: 'top' | 'bottom'; value: number }
  }
  show_avatar: boolean
  show_user_avatar: boolean
}

/** 智能体登录认证配置；保留后端返回的其他认证字段。 */
export interface ApplicationAuthenticationConfig extends Dict<unknown> {
  type?: 'login' | 'password'
  login_value?: string[]
  max_attempts?: number
  // TODO：默认登录方式、账号锁定字段待后台联调。
  default_value?: string
  failed_attempts?: number
  lock_time?: number
}

/** 智能体公开访问凭证与访问限制配置。 */
export interface ApplicationAccessToken extends Partial<ApplicationDisplaySetting> {
  application_id: string
  access_token: string
  is_active: boolean
  access_num: number
  white_active: boolean
  white_list: string[]
  authentication?: boolean
  authentication_value?: ApplicationAuthenticationConfig | null
}

/** 智能体访问配置修改或令牌重置参数。 */
export interface ApplicationAccessTokenPayload {
  show_source?: boolean
  show_exec?: boolean
  is_active?: boolean
  access_token_reset?: boolean
  access_num?: number
  white_active?: boolean
  white_list?: string[]
  language?: string | null
  authentication?: boolean
  authentication_value?: ApplicationAuthenticationConfig
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
  file_upload_enable?: boolean
  file_upload_setting?: Record<string, unknown>
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

/** 智能体概览的两类用户排行。 */
export type ApplicationRankingKind = 'userTokens' | 'questions'
