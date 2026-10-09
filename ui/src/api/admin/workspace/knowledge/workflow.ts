import type { ParamsPage, ResponsePage } from '../../core/types'
import type LogicFlow from '@logicflow/core'
import { get, post, put, getExportFile } from '../../core/request'
import type {
  DefaultModelSettingPayload,
  Dict,
  KnowledgeExecutionRecord,
  KnowledgeWorkflowAction,
  KnowledgeWorkflowDebugPayload,
  KnowledgeWorkflowDetail,
  WorkflowStoreTemplate,
  WorkflowVersion,
  WorkflowVersionPayload,
} from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

type KnowledgeWorkflowPayload =
  | { default_model_setting?: DefaultModelSettingPayload; work_flow: LogicFlow.GraphConfigData; work_flow_template?: never }
  | { work_flow_template: WorkflowStoreTemplate; work_flow?: never }

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/knowledge`
}

/** 保存知识库工作流。 */
const putKnowledgeWorkflow = (knowledgeId: string, payload: KnowledgeWorkflowPayload) => {
  return put<KnowledgeWorkflowPayload, KnowledgeWorkflowDetail>(`${getPrefix()}/${knowledgeId}/workflow`, payload)
}

/** 发布知识库工作流。 */
const putKnowledgeWorkflowPublish = (knowledgeId: string) => {
  return put<undefined, boolean>(`${getPrefix()}/${knowledgeId}/publish`)
}

/** 获取数据源节点的动态表单配置。 */
const getKnowledgeWorkflowFormList = (knowledgeId: string, type: 'local' | 'tool', id: string, node: Dict<unknown>) => {
  return post<{ node: Dict<unknown> }, Dict<unknown>[]>(`${getPrefix()}/${knowledgeId}/datasource/${type}/${id}/form_list`, { node })
}

/** 提交知识库工作流调试任务。 */
const postKnowledgeWorkflowDebug = (knowledgeId: string, payload: KnowledgeWorkflowDebugPayload) => {
  return post<KnowledgeWorkflowDebugPayload, KnowledgeWorkflowAction>(`${getPrefix()}/${knowledgeId}/debug`, payload)
}

/** 获取知识库工作流执行详情，供调试轮询和执行记录共用。 */
const getKnowledgeWorkflowAction = (knowledgeId: string, actionId: string) => {
  return get<KnowledgeWorkflowAction>(`${getPrefix()}/${knowledgeId}/action/${actionId}`)
}

/** 取消知识库工作流执行任务。 */
const postCancelKnowledgeWorkflowAction = (knowledgeId: string, actionId: string) => {
  return post<undefined, boolean>(`${getPrefix()}/${knowledgeId}/action/${actionId}/cancel`)
}

/** 导出知识库工作流文件，不包含知识库文档。 */
const exportKnowledgeWorkflow = (knowledgeId: string, name: string) => getExportFile(`${name}.kbwf`, `${getPrefix()}/${knowledgeId}/workflow/export`)

/** 获取知识库发布历史，按发布时间倒序返回完整版本快照。 */
const getWorkflowVersions = (knowledgeId: string) => get<WorkflowVersion[]>(`${getPrefix()}/${knowledgeId}/knowledge_version`)

/** 修改知识库历史版本标题和更新说明，更新说明需要服务端支持 description 字段。 */
const putWorkflowVersion = (knowledgeId: string, versionId: string, data: WorkflowVersionPayload) =>
  put<WorkflowVersionPayload, WorkflowVersion>(`${getPrefix()}/${knowledgeId}/knowledge_version/${versionId}`, data)

/** 获取知识库工作流执行记录分页，支持发起人和状态筛选。 */
const getKnowledgeExecutionRecordPage = (knowledgeId: string, page: ParamsPage, query?: Dict<unknown>) =>
  get<ResponsePage<KnowledgeExecutionRecord>>(`${getPrefix()}/${knowledgeId}/action/${page.currentPage}/${page.pageSize}`, query)

export default {
  getKnowledgeExecutionRecordPage,
  getWorkflowVersions,
  putWorkflowVersion,
  exportKnowledgeWorkflow,
  putKnowledgeWorkflow,
  putKnowledgeWorkflowPublish,
  getKnowledgeWorkflowFormList,
  postKnowledgeWorkflowDebug,
  getKnowledgeWorkflowAction,
  postCancelKnowledgeWorkflowAction,
}
