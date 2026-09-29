/** 触发器、工具和知识库工作流执行记录共用的状态展示配置。 */
import { STATE_TYPES } from '@/api/enums'
import type { State } from '@/api/types'
import type { StatusLabelOptions } from '@/components/global/mk-status-label/types'

export const EXECUTION_STATUS_OPTIONS: Record<State, StatusLabelOptions> = {
  [STATE_TYPES.PENDING]: { type: 'loading', label: '排队中' },
  [STATE_TYPES.STARTED]: { type: 'loading', label: '执行中' },
  [STATE_TYPES.SUCCESS]: { type: 'success', label: '成功' },
  [STATE_TYPES.FAILURE]: { type: 'failure', label: '失败' },
  [STATE_TYPES.REVOKE]: { type: 'loading', label: '取消中' },
  [STATE_TYPES.REVOKED]: { type: 'failure', label: '已取消' },
  [STATE_TYPES.TRIGGER_ERROR]: { type: 'failure', label: '触发失败' },
}
