/** 执行记录接口状态；文档任务阶段在所属 View 中维护。 */
export const STATE_TYPES = {
  PENDING: 'PENDING',
  STARTED: 'STARTED',
  SUCCESS: 'SUCCESS',
  FAILURE: 'FAILURE',
  REVOKE: 'REVOKE',
  REVOKED: 'REVOKED',
  TRIGGER_ERROR: 'TRIGGER_ERROR',
} as const
