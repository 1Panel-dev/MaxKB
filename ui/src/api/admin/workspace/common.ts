import { get } from '../core/request'
import type { Dict, WorkspaceUserOption } from '@/api/types'
import { getWorkspaceId } from '@/utils/workspace-context'

/** 获取当前工作空间下的用户选项。 */
const getAllUsers = (query?: Dict<unknown>) => {
  const workspaceId = getWorkspaceId()
  return get<WorkspaceUserOption[]>(`/workspace/${workspaceId}/user_list`, query)
}

export default {
  getAllUsers,
}
