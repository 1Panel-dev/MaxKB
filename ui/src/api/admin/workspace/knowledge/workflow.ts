import type LogicFlow from '@logicflow/core'
import { get, post, put } from '../../core/request'
import type { LoadingTarget } from '../../core/types'
import type {
  DefaultModelSettingPayload,
  Dict,
  KnowledgeItem,
  KnowledgeType,
  KnowledgeWorkflowAction,
  KnowledgeWorkflowDebugPayload,
  KnowledgeWorkflowDetail,
} from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

interface KnowledgeWorkflowPayload {
  default_model_setting?: DefaultModelSettingPayload
  work_flow: LogicFlow.GraphConfigData
}

interface CreateKnowledgeWorkflowPayload {
  name: string
  desc?: string
  folder_id: string
  type: KnowledgeType
  work_flow: LogicFlow.GraphConfigData
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
const postKnowledgeUploadFile = (knowledgeId: string, file: File, loading?: LoadingTarget) => {
  const payload = new FormData()
  payload.append('file', file)
  payload.append('source_id', knowledgeId)
  payload.append('source_type', 'KNOWLEDGE')
  return post<FormData, string>('/oss/file', payload, undefined, loading)
}

/** 获取数据源节点的动态表单配置。 */
const getKnowledgeWorkflowFormList = (
  knowledgeId: string,
  type: 'local' | 'tool',
  id: string,
  node: Dict<unknown>,
  loading?: LoadingTarget,
) => {
  return post<{ node: Dict<unknown> }, Dict<unknown>[]>(`${getPrefix()}/${knowledgeId}/datasource/${type}/${id}/form_list`, { node }, undefined, loading)
}

/** 提交知识库工作流调试任务。 */
const postKnowledgeWorkflowDebug = (knowledgeId: string, payload: KnowledgeWorkflowDebugPayload, loading?: LoadingTarget) => {
  return post<KnowledgeWorkflowDebugPayload, KnowledgeWorkflowAction>(`${getPrefix()}/${knowledgeId}/debug`, payload, undefined, loading)
}

/** 轮询知识库工作流调试任务详情。 */
const getKnowledgeWorkflowAction = (knowledgeId: string, actionId: string, loading?: LoadingTarget) => {
  return get<KnowledgeWorkflowAction>(`${getPrefix()}/${knowledgeId}/action/${actionId}`, undefined, loading)
}

/** 取消知识库工作流调试任务。 */
const postCancelKnowledgeWorkflowAction = (knowledgeId: string, actionId: string, loading?: LoadingTarget) => {
  return post<undefined, boolean>(`${getPrefix()}/${knowledgeId}/action/${actionId}/cancel`, undefined, undefined, loading)
}

export default {
  postKnowledgeWorkflow,
  putKnowledgeWorkflow,
  putKnowledgeWorkflowPublish,
  postKnowledgeUploadFile,
  getKnowledgeWorkflowFormList,
  postKnowledgeWorkflowDebug,
  getKnowledgeWorkflowAction,
  postCancelKnowledgeWorkflowAction,
}
