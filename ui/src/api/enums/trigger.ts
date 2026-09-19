/** 触发器类型。 */
export const TRIGGER_TYPE = {
  SCHEDULED: 'SCHEDULED',
  EVENT: 'EVENT',
} as const

/** 定时触发周期。 */
export const TRIGGER_SCHEDULE_TYPE = { DAILY: 'daily', WEEKLY: 'weekly', MONTHLY: 'monthly', INTERVAL: 'interval', CRON: 'cron' } as const
