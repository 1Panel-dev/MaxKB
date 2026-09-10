import type {
  RESOURCE_TYPE,
  TRIGGER_SCHEDULE_TYPE,
  TRIGGER_PARAMETER_SOURCE,
  TRIGGER_BODY_TYPE,
  TRIGGER_INTERVAL_UNIT,
  TRIGGER_TYPE,
} from '@/api/enums'

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
  source: (typeof TRIGGER_PARAMETER_SOURCE)[keyof typeof TRIGGER_PARAMETER_SOURCE]
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
  type: (typeof TRIGGER_BODY_TYPE)[keyof typeof TRIGGER_BODY_TYPE]
  desc?: string
  required?: boolean
}
export interface TriggerSetting {
  schedule_type?: (typeof TRIGGER_SCHEDULE_TYPE)[keyof typeof TRIGGER_SCHEDULE_TYPE]
  interval_unit?: (typeof TRIGGER_INTERVAL_UNIT)[keyof typeof TRIGGER_INTERVAL_UNIT]
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
