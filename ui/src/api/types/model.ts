/** Workspace 模型与工具页面共用的业务类型。 */

import { MODEL_STATUS } from '@/api/enums'
import type { Dict } from './common'
import type { DynamicFormField } from './common'

export type ModelStatus = (typeof MODEL_STATUS)[keyof typeof MODEL_STATUS]

/** 智能体默认模型配置支持的模型类别。 */
export type DefaultModelType = 'LLM' | 'TTS' | 'STT' | 'IMAGE' | 'TTI' | 'TTV' | 'ITV' | 'RERANKER'

export interface ModelConfig {
  model_id?: string
  model_params_setting?: Dict<unknown>
}

export type DefaultModelSettingPayload = Partial<Record<DefaultModelType, ModelConfig>>

export interface ModelProviderItem {
  icon: string
  name: string
  provider: string
}

export interface ModelItem {
  create_time?: string
  id: string
  meta?: Record<string, unknown>
  model_name: string
  model_type: string
  name: string
  nick_name?: string
  provider: string
  source?: 'shared' | 'workspace'
  status: ModelStatus
  user_id?: string
  username?: string
  workspace_id?: string
}

export interface WorkspaceUserOption {
  id: string
  nick_name: string
}

export interface ModelPayload {
  credential: Record<string, unknown>
  model_name: string
  model_params_form?: DynamicFormField[]
  model_type: string
  name: string
  provider: string
}

export interface BaseModelOption {
  desc?: string
  model_type: string
  name: string
}

export interface ModelTypeOption {
  key: string
  value: string
}
