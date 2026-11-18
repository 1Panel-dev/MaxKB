/** 文档状态展示、筛选配置及任务运行状态判断。 */
import { DOCUMENT_TASK_STATE, DOCUMENT_TASK_TYPE, STATE_TYPES } from '@/api/enums'
import type { DocumentItem, DocumentTaskType } from '@/api/types'
import type { StatusLabelType } from '@/components/global/mk-status-label/types'

// 文档展示阶段独立于执行记录接口状态，筛选值不直接提交给后端。
export const DOCUMENT_STATUS_OPTIONS = {
  [STATE_TYPES.PENDING]: { type: 'loading', labelKey: 'common.status.pending' },
  [STATE_TYPES.STARTED]: { type: 'loading', labelKey: 'common.status.running' },
  EMBEDDING: { type: 'loading', labelKey: 'knowledge.document.status.embedding' },
  GENERATE: { type: 'loading', labelKey: 'knowledge.document.status.generate' },
  SYNC: { type: 'loading', labelKey: 'knowledge.document.status.sync' },
  TOKENIZE: { type: 'loading', labelKey: 'knowledge.document.status.tokenize' },
  [STATE_TYPES.SUCCESS]: { type: 'success', labelKey: 'common.status.success' },
  [STATE_TYPES.FAILURE]: { type: 'failure', labelKey: 'common.status.failure' },
  [STATE_TYPES.REVOKE]: { type: 'loading', labelKey: 'common.status.canceling' },
  [STATE_TYPES.REVOKED]: { type: 'failure', labelKey: 'common.status.canceled' },
} satisfies Record<string, { type: StatusLabelType; labelKey: string }>

interface DocumentStatusFilter {
  value: keyof typeof DOCUMENT_STATUS_OPTIONS
  status: (typeof DOCUMENT_TASK_STATE)[keyof typeof DOCUMENT_TASK_STATE]
  task_type?: (typeof DOCUMENT_TASK_TYPE)[keyof typeof DOCUMENT_TASK_TYPE]
}
export const DOCUMENT_STATUS_FILTER_OPTIONS: DocumentStatusFilter[] = [
  { value: STATE_TYPES.SUCCESS, status: DOCUMENT_TASK_STATE.SUCCESS },
  { value: STATE_TYPES.FAILURE, status: DOCUMENT_TASK_STATE.FAILURE },
  {
    value: 'EMBEDDING',
    status: DOCUMENT_TASK_STATE.STARTED,
    task_type: DOCUMENT_TASK_TYPE.EMBEDDING,
  },
  {
    value: 'TOKENIZE',
    status: DOCUMENT_TASK_STATE.STARTED,
    task_type: DOCUMENT_TASK_TYPE.TOKENIZE,
  },
  { value: STATE_TYPES.PENDING, status: DOCUMENT_TASK_STATE.PENDING },
  {
    value: 'GENERATE',
    status: DOCUMENT_TASK_STATE.STARTED,
    task_type: DOCUMENT_TASK_TYPE.GENERATE_PROBLEM,
  },
]

/** 按状态字符串从右起的任务位置判断是否排队或执行中；缺少文档或状态时返回 false。 */
export function isDocumentTaskRunning(document: DocumentItem | undefined, taskType: DocumentTaskType): boolean {
  const state = document?.status?.at(-taskType)
  return state === DOCUMENT_TASK_STATE.PENDING || state === DOCUMENT_TASK_STATE.STARTED
}
