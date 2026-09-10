/** 触发器类型。 */
export const TRIGGER_TYPE = {
  SCHEDULED: 'SCHEDULED',
  EVENT: 'EVENT',
} as const

/** 定时触发周期。 */
export const TRIGGER_SCHEDULE_TYPE = { DAILY: 'daily', WEEKLY: 'weekly', MONTHLY: 'monthly', INTERVAL: 'interval', CRON: 'cron' } as const
/** 触发任务参数来源。 */
export const TRIGGER_PARAMETER_SOURCE = { CUSTOM: 'custom', REFERENCE: 'reference' } as const
/** 事件请求参数类型。 */
export const TRIGGER_BODY_TYPE = { STRING: 'string', INT: 'int', DICT: 'dict', ARRAY: 'array', FLOAT: 'float', BOOLEAN: 'boolean' } as const
/** 定时间隔单位。 */
export const TRIGGER_INTERVAL_UNIT = { MINUTES: 'minutes', HOURS: 'hours' } as const
