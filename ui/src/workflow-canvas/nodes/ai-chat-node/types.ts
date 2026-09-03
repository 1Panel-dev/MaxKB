import type { ApplicationDetail, ToolItem } from '@/api/types'

export type AiModelSource = 'custom' | 'default' | 'reference'
export type DialogueSource = 'NODE' | 'WORKFLOW'
export type McpSource = 'custom' | 'referencing'

export interface AiModelSetting {
  model_id: string
  model_id_reference: string[]
  model_id_type: AiModelSource
  model_params_setting: Record<string, unknown>
}

export interface PromptSetting {
  prompt: string
  system: string
}

export interface HistorySetting {
  dialogue_number: number
  dialogue_type: DialogueSource
}

export interface VisionSetting {
  image_list: string[]
  video_list: string[]
  vision: boolean
}

export interface ReasoningSetting {
  reasoning_content_enable: boolean
  reasoning_content_end: string
  reasoning_content_start: string
}

export interface McpSetting {
  mcp_servers: string
  mcp_source: McpSource
  mcp_tool_ids: string[]
}

export interface ResourceSetting extends McpSetting {
  application_ids: string[]
  mcp_output_enable: boolean
  skill_tool_ids: string[]
  tool_ids: string[]
}

export interface AiChatNodeForm extends AiModelSetting, HistorySetting, PromptSetting, ResourceSetting, VisionSetting {
  is_result: boolean
  model_setting: ReasoningSetting
}

export type ToolResourceOption = Pick<ToolItem, 'desc' | 'icon' | 'id' | 'name' | 'source' | 'tool_type'>
export type ApplicationResourceOption = Pick<ApplicationDetail, 'desc' | 'icon' | 'id' | 'name'>
export type ResourceOption = ToolResourceOption | ApplicationResourceOption
