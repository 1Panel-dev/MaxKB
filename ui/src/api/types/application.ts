/** Workspace 智能体列表及其卡片共用的业务类型。 */

import type LogicFlow from '@logicflow/core'
import { APPLICATION_TYPE } from '@/api/enums'

export type ApplicationType = (typeof APPLICATION_TYPE)[keyof typeof APPLICATION_TYPE]

export interface ApplicationDetail {
  create_time?: string
  desc?: string | null
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
  work_flow?: LogicFlow.GraphData
  model_params_setting?: Record<string, unknown>
  tts_model_params_setting?: Record<string, unknown>
  stt_model_params_setting?: Record<string, unknown>
  stt_model_id?: string
  tts_model_id?: string
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
  long_term_model_id?: string
  long_term_model_params_setting?: Record<string, unknown>
  long_term_trigger_setting?: Record<string, unknown>
  long_term_trigger_type?: string
}
