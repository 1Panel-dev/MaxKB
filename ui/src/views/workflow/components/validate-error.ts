import { formatValidationError } from '@/workflow-canvas/ai-generate/tools/node'
import { MsgError } from '@/utils/message'

/** 提示画布 validate() 的拒绝原因；结构错误（如分支未连接）不会在节点内标红，必须在此提示。 */
export function showWorkflowValidateError(error: unknown) {
  MsgError(error instanceof Error ? error.message : formatValidationError(error))
}
