import { del, get, post } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type {
  CreateWorkspaceMemberParamsItem,
  RequestParams,
  WorkspaceItem,
  WorkspaceMemberItem,
} from '@/api/types'

const prefix = '/system/workspace'

/** 首页头部工作空间列表 | 系统管理的工作空间模块 */
// TODO 工作空间管理员接口 /workspace 未区分
export function getSystemWorkspaceList() {
  return get<WorkspaceItem[]>(prefix)
}

/** 获取工作空间成员列表 **/
// TODO 工作空间管理员接口 /workspace 未区分

export function getWorkspaceMemberList(
  workspace_id: string,
  page: ParamsPage,
  query?: RequestParams,
) {
  return get<ResponsePage<WorkspaceMemberItem>>(
    `${prefix}/${workspace_id}/user_list/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 新建或更新工作空间。 */
export function postWorkspace(workspace: WorkspaceItem) {
  return post<WorkspaceItem, boolean>(prefix, workspace)
}

/** 删除工作空间前校验。 */
export function getWorkspaceDeleteCheck(workspaceId: string) {
  return get<unknown>(`${prefix}/${workspaceId}/check`)
}

/** 删除工作空间。 */
export function deleteWorkspace(workspaceId: string) {
  return del<boolean>(`${prefix}/${workspaceId}`)
}

/** 新增工作空间成员。 */
export function postWorkspaceMembers(
  workspaceId: string,
  members: CreateWorkspaceMemberParamsItem[],
) {
  return post<CreateWorkspaceMemberParamsItem[], boolean>(
    `${prefix}/${workspaceId}/add_member`,
    members,
  )
}

/** 移除工作空间成员。 */
export function postRemoveWorkspaceMember(workspaceId: string, userRelationId: string) {
  return post<undefined, boolean>(`${prefix}/${workspaceId}/remove_member/${userRelationId}`)
}

export default {
  deleteWorkspace,
  getSystemWorkspaceList,
  getWorkspaceMemberList,
  getWorkspaceDeleteCheck,
  postRemoveWorkspaceMember,
  postWorkspace,
  postWorkspaceMembers,
}
