import type { KNOWLEDGE_SYNC_STATUS, SCHEDULE_TYPE } from '@/api/enums'
import type { KnowledgeSyncType } from './knowledge'

export type KnowledgeSyncScheduleType = (typeof SCHEDULE_TYPE)[keyof typeof SCHEDULE_TYPE]
export type KnowledgeSyncStatus = (typeof KNOWLEDGE_SYNC_STATUS)[keyof typeof KNOWLEDGE_SYNC_STATUS]

/** 知识库定时同步设置，时间为 HH:mm，周日期使用 1（周一）至 7（周日）。 */
export interface KnowledgeSyncSetting {
  enabled: boolean
  schedule_type: KnowledgeSyncScheduleType
  sync_type: KnowledgeSyncType
  time?: string[]
  days?: number[]
  interval_unit?: 'minutes' | 'hours'
  interval_value?: number
  cron_expression?: string
}

/** 知识库同步执行日志，涵盖手动与定时任务。 */
export interface KnowledgeSyncLog {
  id: string
  create_time: string
  update_time: string
  sync_type: KnowledgeSyncType
  trigger_type: 'manual' | 'scheduled'
  status: KnowledgeSyncStatus
  total_count: number
  synced_count: number
  skipped_count: number
  deleted_count: number
  failed_count: number
  duration_ms: number
  duration_seconds: number
  message: string
}
