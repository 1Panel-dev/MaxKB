import { get } from '../core/request'
import type { SelectOption } from '@/types'

const prefix = '/system/workspace'

/** 首页头部工作空间列表。 */
// TODO 工作空间管理员接口 /workspace 未区分
export function getSystemWorkspaceList() {
  return get<SelectOption[]>(prefix)
}

export default {
  getSystemWorkspaceList,
}
