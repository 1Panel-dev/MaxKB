/** 提供文档任务运行状态判断，供页面和文档 Action 复用。 */
import { DOCUMENT_TASK_STATE } from '@/api/enums'
import type { DocumentItem, DocumentTaskType } from '@/api/types'

/** 按状态字符串从右起的任务位置判断是否排队或执行中；缺少文档或状态时返回 false。 */
export function isDocumentTaskRunning(document: DocumentItem | undefined, taskType: DocumentTaskType): boolean {
  const state = document?.status?.at(-taskType)
  return state === DOCUMENT_TASK_STATE.PENDING || state === DOCUMENT_TASK_STATE.STARTED
}
