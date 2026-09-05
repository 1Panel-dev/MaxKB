import type { TRIGGER_TYPE } from '@/api/enums'

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
