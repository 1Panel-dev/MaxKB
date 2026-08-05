import { get } from '../core/request'
import type { WorkspaceItem } from '@/types'

const prefix = '/system/workspace'

/** 获取系统管理工作空间列表。 */
// TO DO 工作空间管理员接口 /workspace 未区分
export function getSystemWorkspaceList() {
  return get<WorkspaceItem[]>(prefix)
}

export default {
  getSystemWorkspaceList,
}
