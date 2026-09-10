import type { ToolType } from '@/api/types'

/** 打开抽屉时传入的资源快照。 */
export interface RelatedResourceTarget {
  id: string
  workspace_id: string
  name: string
  icon?: string | null
  type?: string | number
  tool_type?: ToolType
  provider?: string
}
