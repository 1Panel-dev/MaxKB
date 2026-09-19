import type { State } from './state'
import type { RESOURCE_TYPE, TRIGGER_SCHEDULE_TYPE, TRIGGER_TYPE } from '@/api/enums'

export type TriggerType = (typeof TRIGGER_TYPE)[keyof typeof TRIGGER_TYPE]

/** 触发器分页列表中的关联任务。 */
export interface TriggerTask {
  type: string
  name: string | null
  icon: string | null
}

/** 触发器分页列表记录。 */
export interface Trigger {
  id: string
  name: string
  desc: string
  trigger_type: TriggerType
  is_active: boolean
  next_run_time: string | null
  trigger_task: TriggerTask[]
  create_user: string | null
  create_time: string
}

export type TriggerTaskSource = typeof RESOURCE_TYPE.APPLICATION | typeof RESOURCE_TYPE.TOOL
export interface TriggerParameter {
  source: 'custom' | 'reference'
  value: string | string[]
}
export type TriggerParameters = Record<string, TriggerParameter | Record<string, TriggerParameter>>
export interface TriggerTaskPayload {
  id?: string
  source_type: TriggerTaskSource
  source_id: string
  is_active?: boolean
  parameter: TriggerParameters
  meta?: Record<string, unknown>
}
export interface TriggerBodyField {
  field: string
  type: 'string' | 'int' | 'dict' | 'array' | 'float' | 'boolean'
  desc?: string
  required?: boolean
}
export interface TriggerSetting {
  schedule_type?: (typeof TRIGGER_SCHEDULE_TYPE)[keyof typeof TRIGGER_SCHEDULE_TYPE]
  interval_unit?: 'minutes' | 'hours'
  interval_value?: number
  days?: (number | string)[]
  time?: string[]
  cron_expression?: string
  token?: string
  body?: TriggerBodyField[]
}
export interface TriggerPayload {
  id: string
  name: string
  desc: string
  trigger_type: TriggerType
  trigger_setting: TriggerSetting
  trigger_task: TriggerTaskPayload[]
  is_active?: boolean
  meta?: Record<string, unknown>
}
export interface TriggerDetail extends TriggerPayload {
  application_task_list?: Partial<import('./application').ApplicationDetail>[]
  tool_task_list?: Partial<import('./tool').ToolItem>[]
}

export interface TriggerTaskRecord {
  id: string
  trigger_id: string
  trigger_task_id: string
  source_id: string
  source_type: TriggerTaskSource
  source_name: string | null
  source_icon: string | null
  type: string | null
  state: State
  run_time: number | null
  create_time: string
}

export interface TriggerTaskRecordDetail {
  state?: State
  run_time?: number
  problem_text?: string
  answer_text?: string
  details?: Record<string, Record<string, unknown>> | Record<string, unknown>[]
  meta?: {
    input?: unknown
    output?: unknown
    err_message?: string
    details?: Record<string, Record<string, unknown>> | Record<string, unknown>[]
  }
}
