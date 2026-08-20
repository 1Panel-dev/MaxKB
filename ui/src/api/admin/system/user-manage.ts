import { del, get, post, put } from '../core/request'
import type { ResponsePage, ParamsPage, PasswordRequest } from '../core/types'
import type {
  RequestParams,
  SystemUser,
  SystemUserPayload,
  SystemUserUpdateRequest,
  BatchSetUserRolesRequest,
  BatchSetUserWorkspaceRolesRequest,
} from '@/api/types'

const prefix = '/user_manage'

/** 获取系统用户分页列表。 */
const getUserManagePage = (page: ParamsPage, query?: RequestParams) => {
  return get<ResponsePage<SystemUser>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)
}

/** 创建系统用户。 */
const postUser = (payload: SystemUserPayload) => {
  return post<SystemUserPayload, SystemUser>(prefix, payload)
}

/** 编辑系统用户。 */
const putUser = (userId: string, payload: SystemUserUpdateRequest) => {
  return put<SystemUserUpdateRequest, SystemUser>(`${prefix}/${userId}`, payload)
}

/** 修改系统用户密码。 */
const putUserPassword = (userId: string, password: PasswordRequest) => {
  return put<PasswordRequest, boolean>(`${prefix}/${userId}/re_password`, password)
}

/** 删除系统用户。 */
const deleteUser = (userId: string) => {
  return del<boolean>(`${prefix}/${userId}`)
}

/** 批量删除系统用户。 */
const postBatchDeleteUsers = (userIds: string[]) => {
  return post<string[], boolean>(`${prefix}/batch_delete`, userIds)
}

/** 专业版批量设置系统用户角色。 */
const postBatchSetUserRoles = (payload: BatchSetUserRolesRequest) => {
  return post<BatchSetUserRolesRequest, boolean>(`${prefix}/batch/add_role`, payload)
}

/** 企业版批量设置系统用户角色及工作空间。 */
const postBatchSetUserWorkspaceRoles = (payload: BatchSetUserWorkspaceRolesRequest) => {
  return post<BatchSetUserWorkspaceRolesRequest, boolean>(`${prefix}/batch/add_role_ee`, payload)
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
}
