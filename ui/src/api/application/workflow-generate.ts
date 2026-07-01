import { postStream } from '@/request/index'
import useStore from '@/stores'

/**
 * 自然语言流式生成工作流
 * 返回原始 fetch Response，由调用方读取 SSE 流（data: {json}\n\n）
 * 事件类型：stage / plan / done / error，done|error 时 is_end=true
 * @param data 请求数据 { description, model_id }
 */
export const generateWorkflowStream: (data: {
  description: string
  model_id: string
}) => Promise<any> = (data) => {
  const { user } = useStore()
  const apiPrefix = (window.MaxKB?.prefix ? window.MaxKB?.prefix : '/admin') + '/api'
  const workspaceId = user.getWorkspaceId()
  return postStream(
    `${apiPrefix}/workspace/${workspaceId}/application/workflow_generate`,
    data,
  )
}
