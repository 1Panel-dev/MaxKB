/** 任务状态的通用展示文案。 */
import { STATE_TYPES } from '@/api/enums'
import type { State } from '@/api/types'

export const STATE_LABELS: Record<State, string> = {
  [STATE_TYPES.PENDING]: '排队中',
  [STATE_TYPES.STARTED]: '执行中',
  [STATE_TYPES.EMBEDDING]: '索引中',
  [STATE_TYPES.GENERATE]: '生成中',
  [STATE_TYPES.SYNC]: '同步中',
  [STATE_TYPES.TOKENIZE]: '分词索引中',
  [STATE_TYPES.SUCCESS]: '成功',
  [STATE_TYPES.FAILURE]: '失败',
  [STATE_TYPES.REVOKE]: '取消中',
  [STATE_TYPES.REVOKED]: '已取消',
  [STATE_TYPES.TRIGGER_ERROR]: '触发失败',
}
