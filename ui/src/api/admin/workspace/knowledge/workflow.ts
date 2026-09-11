import type LogicFlow from '@logicflow/core'
import { put } from '../../core/request'
import type { DefaultModelSettingPayload, KnowledgeWorkflowDetail } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

interface KnowledgeWorkflowPayload {
  default_model_setting?: DefaultModelSettingPayload
  work_flow: LogicFlow.GraphConfigData
}

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

export default { putKnowledgeWorkflow, putKnowledgeWorkflowPublish }
