import { del, get, post, put } from '../core/request'
import type { ResponsePage, ParamsPage, PasswordRequest } from '../core/types'
import type {
  RequestParams,
  SystemUser,
  SystemUserRequest,
  SystemUserUpdateRequest,
  SystemUserOption,
  BatchSetUserRolesRequest,
  BatchSetUserWorkspaceRolesRequest,
} from '@/api/types'

const prefix = '/user_manage'

/** 获取系统用户分页列表。 */
function getUserManagePage(page: ParamsPage, query?: RequestParams) {
  return get<ResponsePage<SystemUser>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)
}

/** 创建系统用户。 */
function postUser(user: SystemUserRequest) {
  return post<SystemUserRequest, SystemUser>(prefix, user)
}

/** 编辑系统用户。 */
function putUser(userId: string, user: SystemUserUpdateRequest) {
  return put<SystemUserUpdateRequest, SystemUser>(`${prefix}/${userId}`, user)
}

/** 修改系统用户密码。 */
function putUserPassword(userId: string, password: PasswordRequest) {
  return put<PasswordRequest, boolean>(`${prefix}/${userId}/re_password`, password)
}

/** 删除系统用户。 */
function deleteUser(userId: string) {
  return del<boolean>(`${prefix}/${userId}`)
}

/** 批量删除系统用户。 */
function postBatchDeleteUsers(userIds: string[]) {
  return post<string[], boolean>(`${prefix}/batch_delete`, userIds)
}

/** 专业版批量设置系统用户角色。 */
function postBatchSetUserRoles(request: BatchSetUserRolesRequest) {
  return post<BatchSetUserRolesRequest, boolean>(`${prefix}/batch/add_role`, request)
}

/** 企业版批量设置系统用户角色及工作空间。 */
function postBatchSetUserWorkspaceRoles(request: BatchSetUserWorkspaceRolesRequest) {
  return post<BatchSetUserWorkspaceRolesRequest, boolean>(`${prefix}/batch/add_role_ee`, request)
}

/** 获得全部用户 */
function getAllUsers(query?: RequestParams) {
  return get<SystemUserOption[]>('/user/list', query)
}

/** 获取空间下的成员用户
 * @param workspaceId 工作空间ID
 * 资源授权  和用户组的 用户下拉列表使用
 */
function getWorkspaceMembers(workspaceId: string, query?: RequestParams) {
  return get<SystemUserOption[]>(`/workspace/${workspaceId}/user_member`, query)
}

export default {
  deleteUser,
  getUserManagePage,
  postUser,
  postBatchDeleteUsers,
  postBatchSetUserRoles,
  postBatchSetUserWorkspaceRoles,
  putUser,
  putUserPassword,
  getAllUsers,
  getWorkspaceMembers,
}
