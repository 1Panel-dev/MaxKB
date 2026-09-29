import { DOCUMENT_TASK_STATE, DOCUMENT_TASK_TYPE, STATE_TYPES } from '@/api/enums'
import type { StatusLabelOptions } from '@/components/global/mk-status-label/types'

// 文档展示阶段独立于执行记录接口状态，筛选值不直接提交给后端。
export const DOCUMENT_STATUS_OPTIONS = {
  [STATE_TYPES.PENDING]: { type: 'loading', label: '排队中' },
  [STATE_TYPES.STARTED]: { type: 'loading', label: '执行中' },
  EMBEDDING: { type: 'loading', label: '索引中' },
  GENERATE: { type: 'loading', label: '生成中' },
  SYNC: { type: 'loading', label: '同步中' },
  TOKENIZE: { type: 'loading', label: '分词索引中' },
  [STATE_TYPES.SUCCESS]: { type: 'success', label: '成功' },
  [STATE_TYPES.FAILURE]: { type: 'failure', label: '失败' },
  [STATE_TYPES.REVOKE]: { type: 'loading', label: '取消中' },
  [STATE_TYPES.REVOKED]: { type: 'failure', label: '已取消' },
} satisfies Record<string, StatusLabelOptions>

interface DocumentStatusFilter {
  label: string
  value: string
  status: (typeof DOCUMENT_TASK_STATE)[keyof typeof DOCUMENT_TASK_STATE]
  task_type?: (typeof DOCUMENT_TASK_TYPE)[keyof typeof DOCUMENT_TASK_TYPE]
}
export const DOCUMENT_STATUS_FILTER_OPTIONS: DocumentStatusFilter[] = [
  { label: DOCUMENT_STATUS_OPTIONS[STATE_TYPES.SUCCESS].label, value: STATE_TYPES.SUCCESS, status: DOCUMENT_TASK_STATE.SUCCESS },
  { label: DOCUMENT_STATUS_OPTIONS[STATE_TYPES.FAILURE].label, value: STATE_TYPES.FAILURE, status: DOCUMENT_TASK_STATE.FAILURE },
  {
    label: DOCUMENT_STATUS_OPTIONS.EMBEDDING.label,
    value: 'EMBEDDING',
    status: DOCUMENT_TASK_STATE.STARTED,
    task_type: DOCUMENT_TASK_TYPE.EMBEDDING,
  },
  {
    label: DOCUMENT_STATUS_OPTIONS.TOKENIZE.label,
    value: 'TOKENIZE',
    status: DOCUMENT_TASK_STATE.STARTED,
    task_type: DOCUMENT_TASK_TYPE.TOKENIZE,
  },
  { label: DOCUMENT_STATUS_OPTIONS[STATE_TYPES.PENDING].label, value: STATE_TYPES.PENDING, status: DOCUMENT_TASK_STATE.PENDING },
  {
    label: DOCUMENT_STATUS_OPTIONS.GENERATE.label,
    value: 'GENERATE',
    status: DOCUMENT_TASK_STATE.STARTED,
    task_type: DOCUMENT_TASK_TYPE.GENERATE_PROBLEM,
  },
]
