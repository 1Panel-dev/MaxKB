import type LogicFlow from '@logicflow/core'
import { get, post, put, getExportFile } from '../../core/request'
import type {
  DefaultModelSettingPayload,
  Dict,
  KnowledgeItem,
  KnowledgeCreatePayload,
  KnowledgeWorkflowTemplate,
  KnowledgeWorkflowAction,
  KnowledgeWorkflowDebugPayload,
  KnowledgeWorkflowDetail,
  WorkflowStoreTemplate,
} from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

type KnowledgeWorkflowPayload =
  | { default_model_setting?: DefaultModelSettingPayload; work_flow: LogicFlow.GraphConfigData; work_flow_template?: never }
  | { work_flow_template: WorkflowStoreTemplate; work_flow?: never }

interface CreateKnowledgeWorkflowPayload extends KnowledgeCreatePayload {
  work_flow: LogicFlow.GraphConfigData
  work_flow_template?: KnowledgeWorkflowTemplate
}

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/knowledge`
}

/** 创建工作流知识库。 */
const postKnowledgeWorkflow = (payload: CreateKnowledgeWorkflowPayload) => {
  return post<CreateKnowledgeWorkflowPayload, KnowledgeItem>(`${getPrefix()}/workflow`, payload)
}

/** 保存知识库工作流。 */
const putKnowledgeWorkflow = (knowledgeId: string, payload: KnowledgeWorkflowPayload) => {
  return put<KnowledgeWorkflowPayload, KnowledgeWorkflowDetail>(`${getPrefix()}/${knowledgeId}/workflow`, payload)
}

/** 发布知识库工作流。 */
const putKnowledgeWorkflowPublish = (knowledgeId: string) => {
  return put<undefined, boolean>(`${getPrefix()}/${knowledgeId}/publish`)
}

/** 上传知识库调试文件，返回文件访问地址（末段为 file_id）。 */
const postKnowledgeUploadFile = (knowledgeId: string, file: File) => {
  const payload = new FormData()
  payload.append('file', file)
  payload.append('source_id', knowledgeId)
  payload.append('source_type', 'KNOWLEDGE')
  return post<FormData, string>('/oss/file', payload)
}

/** 获取数据源节点的动态表单配置。 */
const getKnowledgeWorkflowFormList = (knowledgeId: string, type: 'local' | 'tool', id: string, node: Dict<unknown>) => {
  return post<{ node: Dict<unknown> }, Dict<unknown>[]>(`${getPrefix()}/${knowledgeId}/datasource/${type}/${id}/form_list`, { node })
}

/** 提交知识库工作流调试任务。 */
const postKnowledgeWorkflowDebug = (knowledgeId: string, payload: KnowledgeWorkflowDebugPayload) => {
  return post<KnowledgeWorkflowDebugPayload, KnowledgeWorkflowAction>(`${getPrefix()}/${knowledgeId}/debug`, payload)
}

/** 轮询知识库工作流调试任务详情。 */
const getKnowledgeWorkflowAction = (knowledgeId: string, actionId: string) => {
  return get<KnowledgeWorkflowAction>(`${getPrefix()}/${knowledgeId}/action/${actionId}`)
}

/** 取消知识库工作流调试任务。 */
const postCancelKnowledgeWorkflowAction = (knowledgeId: string, actionId: string) => {
  return post<undefined, boolean>(`${getPrefix()}/${knowledgeId}/action/${actionId}/cancel`)
}

/** 导出知识库工作流文件，不包含知识库文档。 */
const exportKnowledgeWorkflow = (knowledgeId: string, name: string) => getExportFile(`${name}.kbwf`, `${getPrefix()}/${knowledgeId}/workflow/export`)

export default {
  exportKnowledgeWorkflow,
  postKnowledgeWorkflow,
  putKnowledgeWorkflow,
  putKnowledgeWorkflowPublish,
  postKnowledgeUploadFile,
  getKnowledgeWorkflowFormList,
  postKnowledgeWorkflowDebug,
  getKnowledgeWorkflowAction,
  postCancelKnowledgeWorkflowAction,
}
