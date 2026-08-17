import { get } from '../core/request'
import type { RequestParams, WorkspaceUserOption } from '@/api/types'

/** 获取当前工作空间下的用户选项。 */
const getAllUsers = (workspaceId: string, query?: RequestParams) => {
  return get<WorkspaceUserOption[]>(`/workspace/${workspaceId}/user_list`, query)
}

export default {
  getAllUsers,
}
