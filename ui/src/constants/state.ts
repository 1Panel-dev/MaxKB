/** 触发器、工具和知识库工作流执行记录共用的状态展示配置。 */
import type { State } from '@/api/types'
import type { StatusLabelOptions } from '@/components/global/mk-status-label/types'
import { STATE_TYPES } from '@/api/enums'

export const EXECUTION_STATUS_OPTIONS: Record<State, Omit<StatusLabelOptions, 'label'> & { labelKey: string }> = {
  [STATE_TYPES.PENDING]: { type: 'loading', labelKey: 'common.status.pending' },
  [STATE_TYPES.STARTED]: { type: 'loading', labelKey: 'common.status.running' },
  [STATE_TYPES.SUCCESS]: { type: 'success', labelKey: 'common.status.success' },
  [STATE_TYPES.FAILURE]: { type: 'failure', labelKey: 'common.status.failure' },
  [STATE_TYPES.REVOKE]: { type: 'loading', labelKey: 'common.status.canceling' },
  [STATE_TYPES.REVOKED]: { type: 'failure', labelKey: 'common.status.canceled' },
  [STATE_TYPES.TRIGGER_ERROR]: { type: 'failure', labelKey: 'resource.executionRecords.status.triggerFailed' },
}
