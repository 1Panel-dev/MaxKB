/** 触发器、工具和知识库工作流执行记录共用的状态展示配置。 */
import { computed, reactive } from 'vue'
import type { State } from '@/api/types'
import type { StatusLabelOptions } from '@/components/global/mk-status-label/types'
import { STATE_TYPES } from '@/api/enums'
import { t } from '@/locales'

export const EXECUTION_STATUS_OPTIONS: Record<State, StatusLabelOptions> = reactive({
  [STATE_TYPES.PENDING]: { type: 'loading', label: computed(() => t('common.status.pending')) },
  [STATE_TYPES.STARTED]: { type: 'loading', label: computed(() => t('common.status.running')) },
  [STATE_TYPES.SUCCESS]: { type: 'success', label: computed(() => t('common.status.success')) },
  [STATE_TYPES.FAILURE]: { type: 'failure', label: computed(() => t('common.status.failure')) },
  [STATE_TYPES.REVOKE]: { type: 'loading', label: computed(() => t('common.status.canceling')) },
  [STATE_TYPES.REVOKED]: { type: 'failure', label: computed(() => t('common.status.canceled')) },
  [STATE_TYPES.TRIGGER_ERROR]: { type: 'failure', label: computed(() => t('trigger.taskExecution.triggerFailed')) },
})
