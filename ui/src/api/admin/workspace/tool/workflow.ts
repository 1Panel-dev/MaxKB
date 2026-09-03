import type LogicFlow from '@logicflow/core'
import { get, put } from '../../core/request'
import type { ToolWorkflowDetail } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

interface ToolWorkflowPayload {
  work_flow: LogicFlow.GraphConfigData
}

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/tool`
}

/** 获取工具工作流详情。 */
const getToolWorkflow = (toolId: string) => {
  return get<ToolWorkflowDetail>(`${getPrefix()}/${toolId}/workflow`)
}

/** 保存工具工作流。 */
const putToolWorkflow = (toolId: string, payload: ToolWorkflowPayload) => {
  return put<ToolWorkflowPayload, ToolWorkflowDetail>(`${getPrefix()}/${toolId}/workflow`, payload)
}

/** 发布工具工作流。 */
const putToolWorkflowPublish = (toolId: string) => {
  return put<undefined, boolean>(`${getPrefix()}/${toolId}/publish`)
}

export default { getToolWorkflow, putToolWorkflow, putToolWorkflowPublish }
