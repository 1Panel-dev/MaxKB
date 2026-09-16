import type LogicFlow from '@logicflow/core'
import { get, put, postStream } from '../../core/request'
import type { DefaultModelSettingPayload, ToolWorkflowDetail, ToolWorkflowRecord, WorkflowStoreTemplate } from '@/api/types'
import { ADMIN_API_BASE_PATH } from '@/api/constants'
import { getWorkspaceId } from '@/utils/resource-context'

type ToolWorkflowPayload =
  | { default_model_setting?: DefaultModelSettingPayload; work_flow: LogicFlow.GraphConfigData; work_flow_template?: never }
  | { work_flow_template: WorkflowStoreTemplate; work_flow?: never }

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/tool`
}

/** 获取工具工作流详情。 */
const getToolWorkflow = (toolId: string) => {
  return get<ToolWorkflowDetail>(`${getPrefix()}/${toolId}/workflow`)
}

/** 保存工具工作流，或使用商店模板覆盖当前工作流。 */
const putToolWorkflow = (toolId: string, payload: ToolWorkflowPayload) => {
  return put<ToolWorkflowPayload, ToolWorkflowDetail>(`${getPrefix()}/${toolId}/workflow`, payload)
}

/** 发布工具工作流。 */
const putToolWorkflowPublish = (toolId: string) => {
  return put<undefined, boolean>(`${getPrefix()}/${toolId}/publish`)
}

/** 调试已保存的工具工作流，返回 SSE 响应。 */
const postToolWorkflowDebug = (toolId: string, parameters: Record<string, unknown>) =>
  postStream(ADMIN_API_BASE_PATH, `${getPrefix()}/${toolId}/debug`, parameters)

/** 查询工具工作流调试的输出和节点执行记录。 */
const getToolWorkflowRecord = (toolId: string, recordId: string) => get<ToolWorkflowRecord>(`${getPrefix()}/${toolId}/tool_record/${recordId}`)

export default { getToolWorkflow, putToolWorkflow, putToolWorkflowPublish, postToolWorkflowDebug, getToolWorkflowRecord }
