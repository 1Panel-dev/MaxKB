/* eslint-disable @typescript-eslint/no-explicit-any */
import type { WorkflowNodeType } from '@/workflow-canvas/types'

/**
 * 节点执行详情的运行时载荷。字段随节点类型（含循环、工具工作流的嵌套子节点）差异极大，
 * 由后端按节点动态返回，因此以开放索引签名承载动态字段，仅显式声明外层卡片通用的字段。
 * 各节点的 details.vue 直接读取本类型所需字段，待接口契约稳定后再逐节点收敛为精确类型。
 */
export interface ExecutionNodeDetail {
  [key: string]: any
  answer_tokens?: number
  err_message?: string
  message_tokens?: number
  name?: string
  run_time?: number
  status?: number
  type?: WorkflowNodeType
}
