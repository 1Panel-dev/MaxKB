import type LogicFlow from '@logicflow/core'

/** 工作流发布历史的版本快照与展示信息。 */
export interface WorkflowVersion {
  id: string
  name: string
  /** 更新说明；旧版本接口可能不返回。 */
  description?: string | null
  work_flow: LogicFlow.GraphConfigData
  publish_user_name: string
  create_time: string
  update_time: string
}

/** 发布历史的标题和更新说明编辑内容。 */
export interface WorkflowVersionPayload {
  name: string
  description: string
}
