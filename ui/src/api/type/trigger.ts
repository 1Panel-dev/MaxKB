interface TriggerData {
  id?: string
  name?: string
  desc?: string
  trigger_type?: string
  trigger_setting?: Record<string,any>
  meta?: Record<string,any>
  is_active?: boolean
}

export type { TriggerData }
