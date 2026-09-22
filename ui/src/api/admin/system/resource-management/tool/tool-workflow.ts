import type LogicFlow from '@logicflow/core'
import { get, put, postStream } from '../../../core/request'
import type { ParamsPage, ResponsePage } from '../../../core/types'
import type {
  DefaultModelSettingPayload,
  Dict,
  ToolExecutionRecord,
  ToolExecutionRecordDetail,
  ToolWorkflowDetail,
  ToolWorkflowRecord,
  WorkflowStoreTemplate,
  WorkflowVersion,
  WorkflowVersionPayload,
} from '@/api/types'
import { ADMIN_API_BASE_PATH } from '@/api/constants'

type ToolWorkflowPayload =
  | { default_model_setting?: DefaultModelSettingPayload; work_flow: LogicFlow.GraphConfigData; work_flow_template?: never }
  | { work_flow_template: WorkflowStoreTemplate; work_flow?: never }

const prefix = '/system/resource/tool'

/** 获取工具工作流详情。 */
const getToolWorkflow = (toolId: string) => {
  return get<ToolWorkflowDetail>(`${prefix}/${toolId}/workflow`)
}

/** 保存工具工作流，或使用商店模板覆盖当前工作流。 */
const putToolWorkflow = (toolId: string, payload: ToolWorkflowPayload) => {
  return put<ToolWorkflowPayload, ToolWorkflowDetail>(`${prefix}/${toolId}/workflow`, payload)
}

/** 发布工具工作流。 */
const putToolWorkflowPublish = (toolId: string) => {
  return put<undefined, boolean>(`${prefix}/${toolId}/publish`)
}

/** 调试已保存的工具工作流，返回 SSE 响应。 */
const postToolWorkflowDebug = (toolId: string, parameters: Record<string, unknown>) =>
  postStream(ADMIN_API_BASE_PATH, `${prefix}/${toolId}/debug`, parameters)

/** 查询工具工作流调试的输出和节点执行记录。 */
const getToolWorkflowRecord = (toolId: string, recordId: string) => get<ToolWorkflowRecord>(`${prefix}/${toolId}/tool_record/${recordId}`)

/** 获取工具发布历史，按发布时间倒序返回完整版本快照。 */
const getWorkflowVersions = (toolId: string) => get<WorkflowVersion[]>(`${prefix}/${toolId}/tool_version`)

/** 修改工具历史版本标题和更新说明，更新说明需要服务端支持 description 字段。 */
const putWorkflowVersion = (toolId: string, versionId: string, data: WorkflowVersionPayload) =>
  put<WorkflowVersionPayload, WorkflowVersion>(`${prefix}/${toolId}/tool_version/${versionId}`, data)

/** 获取工具执行记录分页，按执行时间倒序返回。 */
const getToolExecutionRecordPage = (toolId: string, page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<ToolExecutionRecord>>(`${prefix}/${toolId}/tool_record/${page.currentPage}/${page.pageSize}`, query)
}

/** 获取工具执行记录的输入输出及节点详情。 */
const getToolExecutionRecordDetail = (toolId: string, recordId: string) => {
  return get<ToolExecutionRecordDetail>(`${prefix}/${toolId}/tool_record/${recordId}`)
}

export default {
  getToolExecutionRecordPage,
  getToolExecutionRecordDetail,
  getWorkflowVersions,
  putWorkflowVersion,
  getToolWorkflow,
  putToolWorkflow,
  putToolWorkflowPublish,
  postToolWorkflowDebug,
  getToolWorkflowRecord,
}
